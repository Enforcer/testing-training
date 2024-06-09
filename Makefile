# command that runs fastapi server

run_buyer:
	uvicorn --host 0.0.0.0 --port 9090 testing_training.machine.buyer_app.app:app --reload

run_resupplier:
	uvicorn --host 0.0.0.0 --port 8080 testing_training.machine.resupplier_app.app:app --reload

