import logging
import yaml

logging.basicConfig(
    filename='logger.log',
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# set up logging to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

docs = {}
with open("utils/marlin_gcode_helper.yml", "r") as stream:
    try:
        docs = (yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        logger.error('Unable to load Marlin Gcode Helper')