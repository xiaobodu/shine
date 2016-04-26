#!/bin/sh

protoc -I=. --python_out=../shine/share/ ./shine.proto
