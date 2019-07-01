#!/bin/bash
sudo apt-get install -y apt-transport-https
check_docker="$(systemctl is-active docker)"
if [ "$check_docker" != "active" ]; then
    sudo systemctl start docker
    sudo systemctl enable docker
fi
sudo curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" >> /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl kubernetes-cni
sudo apt-mark hold kubelet kubeadm kubectl
echo "Installed Kubernetes tools"
#swapoff -a
# Reconfigure Kubelet service
cd $1
sudo cp ./scripts/10-kubeadm.conf /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
chmod 777 /etc/systemd/system/kubelet.service.d/10-kubeadm.conf
systemctl daemon-reload
systemctl restart kubelet
sudo cp ./scripts/config.yaml /tmp/config.yaml
value=$(kubeadm token generate)
# Pass the token value to /tmp/config.yaml
sed -i -e "s/token:/& \"$value\"/" /tmp/config.yaml
# Set the podsubnet and device IP address
sed -i -e "s/podSubnet:/& \"$2\/16\"/" /tmp/config.yaml
sed -i -e "s/advertiseAddress:/& $3/" /tmp/config.yaml
sed -i -e "s/http:\/\//&$3/" /tmp/config.yaml
sed -i -e "/apiServerCertSANs\:/a \- \"$3\"" /tmp/config.yaml

# Initialize the Kubernetes master node
export KUBECONFIG=/etc/kubernetes/admin.conf
kubeadm init --config /tmp/config.yaml --ignore-preflight-errors Swap
echo "Init completed"

# Install an etcd instance
kubectl apply -f https://docs.projectcalico.org/v3.2/getting-started/kubernetes/installation/hosted/etcd.yaml

# Install the RBAC roles required for Calico
kubectl apply -f https://docs.projectcalico.org/v3.2/getting-started/kubernetes/installation/rbac.yaml

# Install Calico
kubectl apply -f https://docs.projectcalico.org/v3.2/getting-started/kubernetes/installation/hosted/calico.yaml

kubectl taint nodes --all node-role.kubernetes.io/master-

# Install the Kubernetes Dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml
kubectl create -f ./scripts/kube-dashboard-access.yaml
echo "Installed Dashboard"

cp ./scripts/launchkubedb@.service /etc/systemd/system/
sudo chmod 777 /etc/systemd/system/launchkubedb@.service
systemctl daemon-reload
systemctl start launchkubedb@\"$3\".service