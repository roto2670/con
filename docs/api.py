"""
doc test
"""

def hello():
  """
  @api {post} /openapi/subdomain/register
              Register subdomain
  @apiVersion 0.0.1
  @apiName register_subdomain
  @apiGroup Subdomain
  @apiPermission developer
  @apiHeader {string} Authorization Access token key.
  @apiHeader {String} Content-Type=application/json
  @apiHeaderExample {json} Header-Example:
      {
        "Authorization": "Bearer (console_token)"
        "Content-Type": "application/json"
      }

  @apiParamExample {string} Request-Body-Example
        {"gadget_id": "(string) gadget id to use",
         "subname": "(string) top level domain name",
         "domain": "(stirng) domain",
         "protocol": "(string) scheme"
         }

        # testsubdomain2ffd9835f5b99643dca use "push.mib.io"
        {"gadget_id": "testsubdomain2ffd9835f5b99643dca"
         "subname": "push",
         "domain": "mib.io",
         "protocol": "http"
        }


  @apiSuccessExample Success-Response:
        HTTP/1.1 200 OK
        {
          "result": True
        }
  """
  return True
