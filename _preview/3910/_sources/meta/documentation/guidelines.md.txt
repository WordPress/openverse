# Documentation Guidelines

Interested in improving our documentation? Here’s what you need to know before
making any changes to the documentation.

<br/>

## Introduction

Openverse API uses [drf-yasg](https://github.com/axnsan12/drf-yasg), which is a
tool that generates real Swagger/OpenAPI 2.0 specifications from a Django Rest
Framework API.

<br/>

## How to Start Contributing

- Run the server locally by following this
  [link](https://github.com/WordPress/openverse-api#running-the-server-locally)
- Update documentation
- Make sure the updates passed the automated tests in this
  [file](https://github.com/WordPress/openverse-api/blob/main/.github/workflows/ci_cd.yml)
- Commit and push
- Create pull request by following
  [GitHub Repo Guidelines](https://opensource.creativecommons.org/contributing-code/github-repo-guidelines/)

<br/>

## Documentation Styles

- All documentation must be written in American English with no contractions.
- Descriptions must be written using simple yet concise explanations.
- Codes are preferred over videos and screenshots.

<br/>

## Cheat Sheet for drf-yasg

This is a quick syntax guide with examples on how to add or update the
documentation for API endpoints.

<br/>

### Operation ID

The name of API endpoint.

**Example**

```
@swagger_auto_schema(operation_id='image_stats')
```

<br/>

### Operation Description

The description for API endpoint.

**Example**

```
image_stats_description = \
  """
  image_stats is an API endpoint to get a list of all content providers
  and their respective number of images in the Openverse catalog.

  You can use this endpoint to get details about content providers
  such as `source_name`, `image_count`, `display_name`, and `source_url`.

  You can refer to Bash's Request Samples for example on how to use
  this endpoint.
  """

@swagger_auto_schema(operation_id='image_stats',
                     operation_description=image_stats_description)
```

<br/>

### Responses

The response received after submitting an API request. The current API
documentation includes response schemas and response samples based on their
response codes.

**Example**

```
image_stats_200_example = {
  "application/json": {
    "source_name": "flickr",
    "image_count": 465809213,
    "display_name": "Flickr",
    "source_url": "https://www.flickr.com"
  }
}

image_stats_response = {
  "200": openapi.Response(
    description="OK",
    examples=image_stats_200_example,
    schema=AboutImageResponse(many=True)
    )
}

@swagger_auto_schema(operation_id='image_stats',
                     operation_description=image_stats_description,
                     responses=image_stats_response)
```

<br/>

### Request Body

The data sent to the server when submitting an API request.

**Example**

```
register_api_oauth2_request = openapi.Schema(
  type=openapi.TYPE_OBJECT,
  required=['name', 'description', 'email'],
  properties={
    'name': openapi.Schema(
      title="Name",
      type=openapi.TYPE_STRING,
      min_length=1,
      max_length=150,
      unique=True,
      description="A unique human-readable name for your application "
                  "or project requiring access to the Openverse API."
    ),
    'description': openapi.Schema(
      title="Description",
      type=openapi.TYPE_STRING,
      min_length=1,
      max_length=10000,
      description="A description of what you are trying to achieve "
                  "with your project using the API. Please provide "
                  "as much detail as possible!"
    ),
    'email': openapi.Schema(
      title="Email",
      type=openapi.TYPE_STRING,
      min_length=1,
      max_length=254,
      format=openapi.FORMAT_EMAIL,
      description="A valid email that we can reach you at if we "
                  "have any questions about your use case or "
                  "data consumption."
    )
  },
  example={
    "name": "My amazing project",
    "description": "To access CC Catalog API",
    "email": "user@example.com"
  }
)

@swagger_auto_schema(operation_id='register_api_oauth2',
                     operation_description=register_api_oauth2_description,
                     request_body=register_api_oauth2_request,
                     responses=register_api_oauth2_response)
```

<br/>

### Code Examples

Code examples on how to use the API endpoints. The current API documentation
provides code examples in Bash.

**Example**

```
image_stats_bash = \
  """
  # Get a list of content providers and their image count
  curl -H "Authorization: Bearer DLBYIcfnKfolaXKcmMC8RIDCavc2hW" http://api.openverse.engineering/v1/sources
  """

@swagger_auto_schema(operation_id='image_stats',
                     operation_description=image_stats_description,
                     responses=image_stats_response,
                     code_examples=[
                     {
                      'lang': 'Bash',
                      'source': image_stats_bash
                     }
                    ])
```
