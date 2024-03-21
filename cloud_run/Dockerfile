FROM grafana/grafana

ENV GF_ANALYTICS_REPORTING_ENABLED=false \
    GF_AUTH_ANONYMOUS_ENABLED=false \
    GF_AUTH_BASIC_ENABLED=false \
    GF_SECURITY_ADMIN_PASSWORD=admin \
    GF_SECURITY_ADMIN_USER=admin \
    GF_SECURITY_DISABLE_GRAVATAR=true \
    GF_SECURITY_ANGULAR_SUPPORT_ENABLED=false \
    GF_USERS_ALLOW_SIGN_UP=false

RUN grafana-cli plugins install grafana-bigquery-datasource

COPY datasources.yml /etc/grafana/provisioning/datasources/
COPY dashboards.yml /etc/grafana/provisioning/dashboards/
# You'll need your own GCP key here. See: https://cloud.google.com/iam/docs/keys-create-delete
COPY gcp.pem /etc/secrets/
COPY default.json /dashboards/

EXPOSE 3000