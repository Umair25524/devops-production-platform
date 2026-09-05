import json
from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer

app = FastAPI(title="E-Commerce Order API")

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


class Order(BaseModel):
    order_id: str
    customer_id: str
    amount: float


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/orders")
def create_order(order: Order):
    producer.send("orders", order.model_dump())
    producer.flush()

    return {
        "message": "Order published successfully",
        "order": order.model_dump()
    }
