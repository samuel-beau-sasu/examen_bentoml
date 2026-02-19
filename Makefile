.PHONY: serve token predict test-api

PORT ?= 3001
SERVICE ?= src.service:RFClassifierService
BASE_URL ?= http://127.0.0.1:$(PORT)

serve:
	uv run bentoml serve $(SERVICE) --port $(PORT)

token:
	@curl -s -X POST "$(BASE_URL)/login" \
		-H "Content-Type: application/json" \
		-d '{"credentials":{"username":"user123","password":"password123"}}' | jq -r '.token'

predict:
	@token=$$(curl -s -X POST "$(BASE_URL)/login" \
		-H "Content-Type: application/json" \
		-d '{"credentials":{"username":"user123","password":"password123"}}' | jq -r '.token'); \
	curl -s -X POST "$(BASE_URL)/predict" \
		-H "Content-Type: application/json" \
		-H "Authorization: Bearer $$token" \
        -d '{"input_data": {"Serial_No": 362,"GRE_Score": 334,"TOEFL_Score": 116,"University_Rating": 4,"SOP": 4.0,"LOR": 3.5,"CGPA": 9.54,"Research": 1}}'; \
	echo

test-api: predict