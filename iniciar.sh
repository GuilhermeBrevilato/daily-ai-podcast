#!/bin/bash
cd /Users/guilherme/Downloads/daily-podcast

# Roda os dois pipelines em paralelo
python3 main.py &
python3 main_noticias.py &

wait
