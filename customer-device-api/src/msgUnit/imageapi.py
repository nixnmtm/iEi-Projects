import os
from flask import jsonify,request,send_file

class imageApi(object):
    def __init__(self,app):
        self.nameMap={
            "ovs":"./app/OVS.png",
            "kubernetes":"./app/kubernetes.png",
            "docker":"./app/docker@1x.png",
            "qemu_kvm":"./app/qemu_kvm.png",
            "vpp":"./app/vpp.png"
        }

        self.defaultImg="./app/bg.png"
        self.project_path = os.path.dirname(os.path.realpath(__file__))
        print(self.project_path)
        app.add_url_rule('/puzzle/api/images/<string:name>', 'getImage', self.get_image, methods=['GET'])

    def get_image(self,name):
        filename="./app/bg.png"
        name=name.lower()
        if name in self.nameMap:
            filename=self.nameMap[name]
        return send_file(filename, mimetype='image/png')
