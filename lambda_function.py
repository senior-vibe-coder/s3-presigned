import os
import boto3
from jinja2 import Template, Environment

s3 = boto3.client("s3")
bucket_name = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    prefix = event.get("queryStringParameters", {}).get("prefix", "")

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    files = [obj["Key"] for obj in response.get("Contents", [])] if "Contents" in response else []

    file_items = [
        f"<li>{file} - <a href='{s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': file}, ExpiresIn=3600)}'>Download</a></li>"
        for file in files
    ]
    file_items_str = "\n".join(file_items)

    config_info = {
        "Bucket": bucket_name
    }

    env = Environment()
    prefix_template = env.from_string(prefix)
    rendered_prefix = prefix_template.render(os=os)

    template_str = """
<h1>Files in bucket {{ bucket_name }}</h1>
<ul>
{{ file_items_str | safe }}
</ul>

<h2>Application Configuration</h2>
<ul>
{% for key, value in config.items() %}
    <li>{{ key }} : {{ value }}</li>
{% endfor %}
</ul>

<p>You searched for: {{ rendered_prefix }}</p>
"""

    template = Template(template_str)
    html = template.render(
        bucket_name=bucket_name,
        file_items_str=file_items_str,
        config=config_info,
        rendered_prefix=rendered_prefix
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
