"""
RESTful endpoint to receive mixer metadata and initiate profile
creation based on Akara output.
"""

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import *
from django.views.decorators.csrf import csrf_exempt

from freemix.dataset.models import parse_profile_json
from freemix.dataset import transform

from django.utils import simplejson as json
from django.conf import settings
from urlparse import urljoin

AKARA_MIX_URL = getattr(settings, "AKARA_MIX_URL",
                        urljoin(transform.AKARA_URL_PREFIX,
                                "mix.freemix.json"))

mixer = transform.AkaraTransformClient(AKARA_MIX_URL)
akara = transform.AkaraTransformClient(transform.AKARA_TRANSFORM_URL)

def extract_content(request):
    return request.POST["mixdata"]

def create_mixed_dataset(use, contents):
    set = parse_profile_json(use, contents)
    url = reverse("dataset_edit",
                  args=[use.username, set.slug])
    return HttpResponseRedirect(url)

@csrf_exempt
@login_required
def mix_data(request):
    if request.method == "POST":
        data = mixer(body=extract_content(request))
        profile = akara(body=json.dumps(data))
        return create_mixed_dataset(request.user, profile)
    else:
        return HttpResponseNotAllowed(['POST'])
