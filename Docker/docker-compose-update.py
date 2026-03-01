import os, sys, subprocess
import yaml

docker_paths = []
containers_upgraded = 0

root_path = sys.argv[1]

print(f"Updating containers in {root_path}...")

try:
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if "docker-compose" in file:
                docker_paths.append(str(os.path.join(root, file)))
except Exception as e:
    print("Incorrect argument! This script requires one argument: the root path of the directory containing the Docker Compose files that describe the containers you wish to update.")
    print(e)
    exit()

for file in docker_paths:
    try:
        # get the current running containers
        docker_ps_output = subprocess.run(['docker', 'ps'], capture_output=True, text=True, shell=False)

        # load the compose.yaml file into a dict
        with open(file, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)

        for container in data['services']:
            if data['services'][container]['container_name'] in docker_ps_output.stdout:
                # run docker compose pull on the docker compose file
                result = subprocess.run(['docker', 'compose', '-f', file, 'pull'], capture_output=True, text=True, shell=False)

                # if pulling is successful, run docker compose up on the file.
                if result.returncode == 0:
                    result = subprocess.run(['docker', 'compose', '-f', file, 'up', '-d'], capture_output=True, text=True, shell=False)
                    if result.returncode == 0:
                        print(f"Successfully updated containers described in {file}")
                        containers_upgraded += 1
                    break

                elif result.returncode != 0:
                    print(f"Error pulling image(s) for {file}: {result.stderr}")
                    break

    except Exception as e:
        print("Error: ", e)

print(f"Updated {containers_upgraded} containers.")