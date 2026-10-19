from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import json
from pathlib import Path

FILE_JSON = Path(__file__).parent / "data.json"

class BahanCreate(BaseModel):
    nama_bahan: str = Field(..., min_length=2)
    kategori: str = Field(...)
    stok: int = Field(..., ge=0)
    satuan: str = Field(...)

class Bahan(BahanCreate):
    id: int

app = FastAPI(title="Dashboard Muji Nugraha - Ganjil")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

default_data = [
    {"id":1,"nama_bahan":"Beras Muji Premium","kategori":"Beras & Biji","stok":55,"satuan":"kg"},
    {"id":2,"nama_bahan":"Ayam Kampung Nugraha","kategori":"Daging","stok":12,"satuan":"kg"},
    {"id":3,"nama_bahan":"Cabai Rawit Muji","kategori":"Bumbu","stok":3,"satuan":"kg"},
    {"id":4,"nama_bahan":"Bawang Merah Brebes","kategori":"Bumbu","stok":0,"satuan":"kg"},
    {"id":5,"nama_bahan":"Tomat Cherry Muji","kategori":"Sayuran","stok":8,"satuan":"kg"},
    {"id":6,"nama_bahan":"Santan Muji Kara","kategori":"Produk Olahan","stok":25,"satuan":"pcs"},
    {"id":7,"nama_bahan":"Telur Ayam Omega Muji","kategori":"Produk Olahan","stok":2,"satuan":"kg"},
    {"id":8,"nama_bahan":"Kangkung Muji Fresh","kategori":"Sayuran","stok":5,"satuan":"ikat"},
    {"id":9,"nama_bahan":"Jahe Merah Muji","kategori":"Bumbu","stok":7,"satuan":"kg"},
    {"id":10,"nama_bahan":"Sapi Wagyu Muji","kategori":"Daging","stok":0,"satuan":"kg"},
    {"id":11,"nama_bahan":"Garam Himalaya Muji","kategori":"Bumbu","stok":15,"satuan":"kg"},
    {"id":12,"nama_bahan":"Bayam Hijau Muji","kategori":"Sayuran","stok":4,"satuan":"ikat"},
    {"id":13,"nama_bahan":"Kecap Manis Muji","kategori":"Produk Olahan","stok":18,"satuan":"liter"},
    {"id":14,"nama_bahan":"Bawang Putih Kating","kategori":"Bumbu","stok":6,"satuan":"kg"},
    {"id":15,"nama_bahan":"Udang Vaname Muji","kategori":"Seafood","stok":9,"satuan":"kg"},
    {"id":16,"nama_bahan":"Wortel Berastagi Muji","kategori":"Sayuran","stok":11,"satuan":"kg"},
    {"id":17,"nama_bahan":"Minyak Goreng Muji","kategori":"Produk Olahan","stok":1,"satuan":"liter"},
    {"id":18,"nama_bahan":"Kunyit Muji","kategori":"Bumbu","stok":20,"satuan":"kg"},
    {"id":19,"nama_bahan":"Jamur Shitake Muji","kategori":"Sayuran","stok":3,"satuan":"pack"},
    {"id":20,"nama_bahan":"Keju Mozzarella Muji","kategori":"Produk Olahan","stok":0,"satuan":"kg"},
    {"id":21,"nama_bahan":"Daun Jeruk Muji","kategori":"Bumbu","stok":13,"satuan":"ikat"},
    {"id":22,"nama_bahan":"Ikan Salmon Muji","kategori":"Seafood","stok":5,"satuan":"kg"},
    {"id":23,"nama_bahan":"Daun Kemangi Muji","kategori":"Sayuran","stok":2,"satuan":"ikat"},
    {"id":24,"nama_bahan":"Lada Hitam Muji","kategori":"Bumbu","stok":14,"satuan":"kg"},
]

def load_data():
    if not FILE_JSON.exists():
        save_data(default_data)
        return default_data
    return json.loads(FILE_JSON.read_text())

def save_data(data):
    FILE_JSON.write_text(json.dumps(data, indent=2))

@app.get("/api/bahan", response_model=List[Bahan])
def get_all():
    return load_data()

@app.post("/api/bahan", response_model=Bahan)
def create(item: BahanCreate):
    data = load_data()
    new_id = max([d["id"] for d in data], default=0) + 1
    new_item = {"id": new_id, **item.model_dump()}
    data.append(new_item)
    save_data(data)
    return new_item

@app.delete("/api/bahan/{item_id}")
def delete(item_id: int):
    data = load_data()
    new_data = [d for d in data if d["id"] != item_id]
    if len(new_data) == len(data):
        raise HTTPException(status_code=404, detail="ID tidak ditemukan")
    save_data(new_data)
    return {"message": "deleted"}

@app.put("/api/bahan/{item_id}", response_model=Bahan)
def update(item_id: int, item: BahanCreate):
    data = load_data()
    for i, d in enumerate(data):
        if d["id"] == item_id:
            data[i] = {"id": item_id, **item.model_dump()}
            save_data(data)
            return data[i]
    raise HTTPException(status_code=404, detail="ID tidak ditemukan")