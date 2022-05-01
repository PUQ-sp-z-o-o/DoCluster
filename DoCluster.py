#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from src.DoCluster_class import DoClusterMng


Cluster = DoClusterMng()
time.sleep(1)
Cluster.MngStartWeb()
time.sleep(1)
Cluster.ApiStartWeb()
time.sleep(1)
Cluster.MngSchedulersStart()
#Cluster.MngSchedulersStart()


