#!/usr/bin/env bash

nvidia-smi --query-gpu=timestamp,pci.bus_id,utilization.gpu,utilization.memory,memory.used --format=csv -lms 100 -f gpu_log_$(date "+%Y-%m-%d-%T").csv

