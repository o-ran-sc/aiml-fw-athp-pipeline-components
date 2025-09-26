# ==================================================================================
#
#       Copyright (c) 2025 Samsung Electronics Co., Ltd. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ==================================================================================
import requests
import argparse
import logging, colorlog


# pipeline_name = "generic_pipeline"
# pipeline_file = "pipeline.yaml"

# Configure colored logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='upload pipeline')
    parser.add_argument('-f', '--file-name', dest='pipeline_file', required=True,
                        action='store', default='pipeline.yaml',
                        help='generated yaml file for pipeline')
    parser.add_argument('-p', '--pipeline-name', dest='pipeline_name', required=True,
                        action='store', default='generic_pipeline',
                        help='target pipeline name')
    parser.add_argument('-i','--ip-address',dest ='ip_address',required=True,action='store',default='localhost',help='Provide Ip address')
    args = parser.parse_args()


    try:
        url = f"http://{args.ip_address}:32002/pipelines/{args.pipeline_name}/upload"
        resp = requests.post(
            url,
            files={"file": open(args.pipeline_file, "rb")},
        )
        logging.info(f"Request URL: {url}")
        logging.debug(f"File Uploaded: {args.pipeline_file}")
        logging.debug(f"Response Status Code: {resp.status_code}")
        logging.debug(f"Response Content: {resp.text}")
        logging.info("Pipeline upload process completed.")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred during the request: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


