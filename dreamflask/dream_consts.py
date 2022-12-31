GENERATED_FOLDER = 'images/img-samples'
WORKBENCH_FOLDER = 'images/img-workbench'
THUMBNAILS_FOLDER = 'images/img-thumbnails'
PLAYGROUND_FOLDER = 'images/img-playground'

IMG_FILES = "dreamflask/images"
JS_FILES = "dreamflask/js"
CSS_FILES = "dreamflask/css"
FAVICON = "dreamflask/icons/favicon.ico"

MODELS_FOLDER = 'models/ldm/stable-diffusion/'

DEV_DB = "sessions_dev.db"
PROD_DB = "sessions_prod.db"

SD_API_PORT = 7860
SD_API_HOST = "http://127.0.0.1"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

OPTIONS_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/options"
UPSCALE_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/extra-single-image"
TXT2IMG_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/txt2img"
IMG2IMG_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/img2img"
PROGRESS_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/progress"
MODELS_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/sd-models"
SAMPLERS_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/samplers"
UPSCALERS_API_URL = f"{SD_API_HOST}:{SD_API_PORT}/sdapi/v1/upscalers"

IMAGE_DIMS = [ f'{8 * n}' for n in range(16, 129, 8) ]

# Common additions for details
PROMPT_EXTRAS = {}
PROMPT_EXTRAS['moods'] = ['amazing', 'eerie', 'epic', 'creepy', 'ominous', 'beautiful', 'dream',
	'peaceful', 'serenity', 'calm', 'inner peace', 'awareness', 'silence', 'noir',
	'expressive', 'dark', 'surreal', 'dramatic', 'serene', 'attractive', 'spectacular',
	'vibrant', 'stunning']

PROMPT_EXTRAS['camera'] = ['f1.8', 'f2', '14mm', '50mm', '85mm', 'low iso', 'high iso', 'film grain',
	'dof', 'depth of field', 'wide angle', 'macro lens', 'soft focus', 'sharp focus', 'chromatic aberration',
	'global illumination', 'subsurface scattering', 'focal length', 'diffuse', 'emissive', 'caustic']

PROMPT_EXTRAS['details'] = ['4k', '8k', 'HD', 'photorealistic', 'hyper detail', 'detailed', 'abstract',
	'cinematic', 'Unreal Engine', 'Octane Rendering', 'V-Ray', 'bokeh', 'contrast',
	'symmetric', 'intricate', 'volumetric lighting', 'soft lightning', 'raytracing', 'colorful',
	'wallpaper', 'fog', 'holography', 'lens flare', 'anamorphic',
	'luminescence', 'rule of thirds', 'center framing', 'blur', 'seemless texture']

PROMPT_EXTRAS['artists'] = ['Bill Watterson', 'Christian Bravery', 'Alex Grey', 'Jacek Yerka', 'Roger Dean', 'HR Giger', 'Gustav Klimt', 'Richard Avedon',
	'Vogue', 'Baron Adolphe De Meyer', 'Alexander Jansson', 'Albert Bierstadt', 'Lee Madgwick',
	'Rembrandt', 'Viktor Antonov', 'Sergey Kolesov', 'Eric Wallis', 'Charlie Bowater',
	'Daniela Uhlig', 'Wlop', 'Gil Elvgren', 'Rebeca Saray', 'Bayard Wu', 'Patrick Demarchelier',
	'Dan Mumford', 'Peter Mohrbacher', 'Jean Basquiat', 'Peter Gric', 'Makoto Shinkai',
	'Daniel Merriam', 'Hubert Robert', 'Jonathan Solter', 'Gerardo Dottori', 'Johfra Bosschart',
	'Beksinski Finnian', 'Vitaly Vulgarov', 'Moebius']

PROMPT_EXTRAS['mediums'] = ['postcard', 'tarot card', 'watercolor', 'gouche', 'matte', 'painting',
	'oil painting', 'color pencil', 'pen and ink', 'photo', 'render',
	'pencil', 'graphite', 'digital', 'lithograph']

PROMPT_EXTRAS['styles'] = ['cyberpunk', 'industrialpunk', 'trending on artstation', 'deviantart', 'fantasy', 'dark fantasy',
	'futuristic', 'folklore', 'concept art', 'witchcore', 'lovecraftian', 'baroque', 'retrofuturism',
	'devilcore', 'vaporwave', 'pixel', 'diffusion', 'fractal', 'fractalism', 'vintage', 'black and white',
	'illustration', 'medeival', 'monochrome', 'noir', 'synthwave', 'darksynth', 'grimdark',
	'aetherpunk', 'CGsociety', 'technopunk']
