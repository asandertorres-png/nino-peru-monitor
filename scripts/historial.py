"""Historial diario del monitor: una fila por dia con el ONI, la TSM semanal y
las anomalias de cada departamento.

    PYTHONPATH=scripts python3 scripts/historial.py              # agrega el estado actual
    PYTHONPATH=scripts python3 scripts/historial.py --reconstruir # ademas, rehace desde git

Cada corrida (cada 6 horas) deja un data/estado.json distinto, pero los
agregados diarios solo cambian una vez al dia, asi que el historial guarda
una fila por fecha (hora de Lima): la ultima corrida del dia reemplaza a las
anteriores. Solo nivel departamental: el provincial multiplicaria por ocho el
tamano del archivo y la interfaz lo consulta rara vez.

Si el archivo no existe, se reconstruye desde los snapshots de estado.json
commiteados en git (el flujo automatico hace un checkout con historia). Asi
el historial arranca con lo que ya se publico y no desde cero.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "data" / "estado.json"
HISTORIAL = RAIZ / "data" / "historial.json"
MAX_DIAS = 400  # ~13 meses; el archivo queda por debajo de 1 MB


def fila_desde_estado(e):
    s = e.get("tsm_semanal") or {}
    reg = s.get("regiones") or {}
    unidades = {}
    for d in e.get("departamentos", []):
        unidades[d["nombre"]] = {
            "pp": d.get("anomalia_precipitacion_pct"),
            "mm": d.get("anomalia_precipitacion_mm"),
            "tx": d.get("anomalia_tmax_c"),
            "al": d.get("nivel_alerta"),
        }
    oni = e.get("oni") or {}
    return {
        "fecha": e["actualizado"][:10],
        "actualizado": e["actualizado"],
        "oni": oni.get("oni"),
        "oni_trimestre": f"{oni.get('trimestre', '?')} {oni.get('anio', '')}".strip(),
        "tsm34": s.get("anomalia"),
        "tsm12": (reg.get("nino12") or {}).get("anomalia"),
        "unidades": unidades,
    }


def cargar():
    if HISTORIAL.exists():
        try:
            return json.loads(HISTORIAL.read_text())
        except json.JSONDecodeError:
            print("aviso: historial ilegible, se rehace", flush=True)
    return {"nivel": "departamento", "una_fila_por": "dia (hora de Lima); la ultima corrida del dia", "dias": []}


def agregar(hist, fila):
    """Inserta o reemplaza la fila de esa fecha; mantiene orden y tope."""
    dias = [d for d in hist["dias"] if d["fecha"] != fila["fecha"]]
    dias.append(fila)
    dias.sort(key=lambda d: d["fecha"])
    hist["dias"] = dias[-MAX_DIAS:]
    hist["desde"] = hist["dias"][0]["fecha"]
    hist["hasta"] = hist["dias"][-1]["fecha"]
    return hist


def snapshots_en_git():
    """Estados commiteados, del mas antiguo al mas reciente."""
    try:
        shas = subprocess.check_output(
            ["git", "log", "--reverse", "--format=%H", "--", "data/estado.json"],
            cwd=RAIZ, text=True).split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    salida = []
    for sha in shas:
        try:
            crudo = subprocess.check_output(["git", "show", f"{sha}:data/estado.json"],
                                            cwd=RAIZ, text=True)
            salida.append(json.loads(crudo))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
    return salida


def main():
    reconstruir = "--reconstruir" in sys.argv or not HISTORIAL.exists()
    hist = cargar()
    if reconstruir:
        previos = snapshots_en_git()
        for e in previos:
            if "actualizado" in e:
                agregar(hist, fila_desde_estado(e))
        print(f"reconstruido desde git: {len(previos)} snapshots", flush=True)
    if ESTADO.exists():
        agregar(hist, fila_desde_estado(json.loads(ESTADO.read_text())))
    if not hist["dias"]:
        raise SystemExit("sin estado que historiar: correr antes actualizar.py")
    HISTORIAL.write_text(json.dumps(hist, ensure_ascii=False, separators=(",", ":")))
    print(f"historial: {len(hist['dias'])} dias, {hist['desde']} -> {hist['hasta']}, "
          f"{HISTORIAL.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
