.PHONY: list test func run
.SILENT: unittest_build_silent db_start db_stop service_build_silent

PG_CONTAINER = la_postgresql_container

DB_HOST = localhost
DB_PORT = 5432
DB_USER = postgres
DB_PASSWORD = password
DB_NAME = lizaalert

SERVICE_DOCKERFILE = Dockerfile_local
SERVICE_IMAGE = la_local_image
SERVICE_CONTAINER  =  la_local_container

TEST_DOCKERFILE = Dockerfile_test
TEST_IMAGE = la_unittest_image
TEST_CONTAINER = la_unittest_container

FUNC_DOCKERFILE = Dockerfile_func
FUNC_IMAGE = la_func_image
FUNC_CONTAINER = la_func_container

CHECK_DOCKERFILE = Dockerfile_check
CHECK_IMAGE = la_check_image
CHECK_CONTAINER = la_check_container

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'


db_start:
	docker run --rm -d \
	--name $(PG_CONTAINER) \
	-p 5432:5432 \
	-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
	-e POSTGRES_USER=$(DB_USER) \
	postgres:13-alpine


db_stop:
	docker stop $(PG_CONTAINER)


unittest_build:
	docker build -f $(TEST_DOCKERFILE) -t $(TEST_IMAGE) .


unittest_build_silent:
	make unittest_build


unittest:
	-make db_stop
	make db_start
	make unittest_build_silent

	docker run --rm --net=host \
	--name $(TEST_CONTAINER) \
	-p 8000:8000 \
	-e DB_HOST=$(DB_HOST) \
	-e DB_NAME=$(DB_NAME) \
	-e DB_PASSWORD=$(DB_PASSWORD) \
	-e DB_USER=$(DB_USER) \
	$(TEST_IMAGE)

	make db_stop


service_build:
	docker build -f $(SERVICE_DOCKERFILE) -t $(SERVICE_IMAGE) .


service_build_silent:
	make service_build


run:
	-make db_stop
	make db_start
	make service_build_silent

	docker run --rm --net=host \
	--name $(SERVICE_CONTAINER) \
	-p 8000:8000 \
	-e DB_HOST=$(DB_HOST) \
	-e DB_NAME=$(DB_NAME) \
	-e DB_PASSWORD=$(DB_PASSWORD) \
	-e DB_USER=$(DB_USER) \
	$(SERVICE_IMAGE)

	make db_stop

func_debug:
	docker build -f $(FUNC_DOCKERFILE) -t $(FUNC_IMAGE) .

	docker run --rm --net=host \
	--name $(FUNC_CONTAINER) \
	-p 8000:8000 \
	-e DB_HOST=$(DB_HOST) \
	-e DB_NAME=$(DB_NAME) \
	-e DB_PASSWORD=$(DB_PASSWORD) \
	-e DB_USER=$(DB_USER) \
	$(FUNC_IMAGE)


func:
	-docker stop $(SERVICE_CONTAINER)
	-make db_stop
	make db_start
	make service_build_silent

	docker run -d --rm --net=host \
	--name $(SERVICE_CONTAINER) \
	-p 8000:8000 \
	-e DB_HOST=$(DB_HOST) \
	-e DB_NAME=$(DB_NAME) \
	-e DB_PASSWORD=$(DB_PASSWORD) \
	-e DB_USER=$(DB_USER) \
	$(SERVICE_IMAGE)

	sleep 3
	make func_debug

	docker stop $(SERVICE_CONTAINER)
	make db_stop


check:
	docker build -f $(CHECK_DOCKERFILE) -t $(CHECK_IMAGE) .
	docker run --rm --name $(CHECK_CONTAINER) $(CHECK_IMAGE)
