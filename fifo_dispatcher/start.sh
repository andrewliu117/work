#!/bin/bash

date
exec nohup python fifo_dispatcher.py &
