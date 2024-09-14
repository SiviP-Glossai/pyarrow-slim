import os
import pathlib
import shutil


base_dir = pathlib.Path(__file__).resolve().parent
out_dir = base_dir / "output"
out_dir.mkdir(exist_ok=True)

tag = "pyarrow-slim"
os.chdir(base_dir)

import docker
print("Connecting to docker daemon")
docker_client = docker.from_env()
print("Successfully connected to docker daemon")

print(
    f"Building docker image: {tag}. This might take several minutes..."
)
cmd = [
    "docker",
    "build",
    "-t",
    tag,
    ".",
    "-f",
    "Dockerfile.amazon_linux",
]
os.system(" ".join(cmd))

print(f"Running docker container of image {tag}")
container = docker_client.containers.run(
    image=tag, remove=True, entrypoint="bash", detach=True, tty=True
)
# run the following command inside container: RUN cp -r /arrow/python/dist /opt/
# and then copy the dist folder to the host machine



print(f"Container running: {container.id}")
file_path_in_docker = "/arrow/python/dist"
zip_path = out_dir / "out.tar.gz"
with open(zip_path, "wb+") as fd:
    print(f"Extracting {file_path_in_docker} from {tag}")
    bits, stat = container.get_archive(file_path_in_docker)
    print(f"Extracted: {stat}")
    for chunk in bits:
        fd.write(chunk)

print(f"Killing Container: {container.id}")
container.kill()

extract_path = out_dir

print(f"Extracting archive to: {extract_path}")
shutil.unpack_archive(zip_path.as_posix(), extract_path)
zip_path.unlink()