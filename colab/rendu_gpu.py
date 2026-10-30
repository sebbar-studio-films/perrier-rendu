# Google Colab (GPU T4) : calcule des images de la pub Perrier avec Blender 5.2 (CUDA/OptiX)
# et télécharge un zip toutes les 10 images. Dans une cellule :
#   FICHIER = "pub_v.blend"; IMAGES = list(range(61, 151))
#   %run /content/repo/colab/rendu_gpu.py
import os, subprocess, zipfile
from google.colab import files
DEPOT = "https://github.com/amineZEZ/perrier-rendu/releases/download/v1/"
g = globals()
FICHIER = g.get("FICHIER", "pub_v.blend")
IMAGES = g.get("IMAGES", list(range(61, 151)))
os.chdir("/content")
if not os.path.exists("blender/blender"):
    subprocess.run(f"wget -q {DEPOT}blender-5.2.2-linux-x64.tar.xz -O b.tar.xz && mkdir -p blender && tar -xf b.tar.xz -C blender --strip-components=1 && rm b.tar.xz", shell=True, check=True)
    subprocess.run("apt-get -qq install -y libxrender1 libxi6 libxkbcommon0 libsm6 libxxf86vm1 libxfixes3 > /dev/null", shell=True)
if not os.path.exists(FICHIER):
    subprocess.run(f"wget -q {DEPOT}{FICHIER} -O {FICHIER}", shell=True, check=True)
GPU = ("import bpy\np=bpy.context.preferences.addons['cycles'].preferences\n"
       "p.compute_device_type='OPTIX'\np.get_devices()\n[setattr(d,'use',True) for d in p.devices]\n"
       "bpy.context.scene.cycles.device='GPU'\n")
open("gpu.py", "w").write(GPU)
os.makedirs("images", exist_ok=True)
lot = []
for f in IMAGES:
    sortie = f"images/img_{f:04d}.png"
    if not os.path.exists(sortie):
        subprocess.run(["blender/blender", "-b", FICHIER, "-P", "gpu.py", "-o", "/content/images/img_####", "-F", "PNG", "-f", str(f)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("image", f, "ok" if os.path.exists(sortie) else "ÉCHEC", flush=True)
    lot.append(sortie)
    if len(lot) == 10 or f == IMAGES[-1]:
        nom = f"perrier_{FICHIER[4]}_{lot[0][-8:-4]}-{lot[-1][-8:-4]}.zip"
        with zipfile.ZipFile(nom, "w") as z:
            for p in lot:
                if os.path.exists(p):
                    z.write(p, os.path.basename(p))
        files.download(nom)
        lot = []
