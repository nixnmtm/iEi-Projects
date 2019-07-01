#!/bin/bash
lsof -i tcp:8001 | grep LISTEN | awk '{print $2}' | xargs kill
systemctl stop launchkubedb@\"$1\".service
kubeadm reset --force
sudo apt-get remove -y --allow-change-held-packages kubelet kubeadm kubectl kubernetes-cni
rm -f /etc/systemd/system/launchkubedb@.service
rm -f /etc/apt/sources.list.d/kubernetes.list
rm -f /tmp/config.yaml
rm -f /root/.kube/config
echo "Uninstalled Kubernetes"
