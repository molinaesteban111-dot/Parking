"""Interfaz de línea de comandos para entrenar y evaluar agentes."""

import argparse

from evaluate import evaluate
from neural_q_learning import train as train_neural
from q_learning import train as train_tabular


parser = argparse.ArgumentParser(description="Experimentos de parking autónomo")
subparsers = parser.add_subparsers(dest="command", required=True)

train_parser = subparsers.add_parser("train", help="Entrena un agente")
train_parser.add_argument("--agent", choices=("q", "nn"), default="q")
train_parser.add_argument("--episodes", type=int, default=500)

eval_parser = subparsers.add_parser("evaluate", help="Compara agentes y genera métricas")
eval_parser.add_argument("--episodes", type=int, default=30)
eval_parser.add_argument("--output", default="metrics.png")

args = parser.parse_args()
if args.command == "train":
    history = train_tabular(args.episodes)[1] if args.agent == "q" else train_neural(args.episodes)
    print(f"Entrenamiento terminado: {len(history)} episodios")
else:
    evaluate(args.episodes, args.output)
