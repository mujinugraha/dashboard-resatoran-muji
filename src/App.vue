<template>
  <div class="container">
    <h1>Dashboard Restoran - Muji Nugraha</h1>
    <p class="sub">Soal A Ganjil - Bahan Baku Dapur</p>

    <div class="status" :class="statusFetch">
      <span v-if="statusFetch === 'loading'">⏳ Loading...</span>
      <span v-if="statusFetch === 'error'"
        >❌ Error: {{ errorMsg }} - pastikan backend jalan</span
      >
      <span v-if="statusFetch === 'success'"
        >✅ Berhasil - {{ sorted.length }} dari
        {{ bahanList.length }} item</span
      >
    </div>

    <!-- 4 TILE WAJIB -->
    <div class="tiles">
      <div class="tile">
        <small>Total Bahan Baku</small><b>{{ totalBahan }}</b>
      </div>
      <div class="tile warn">
        <small>Menipis + Habis</small><b>{{ menipisHabis }}</b>
      </div>
      <div class="tile">
        <small>Jumlah Kategori</small><b>{{ jumlahKategori }}</b>
      </div>
      <div class="tile">
        <small>Total Satuan Stok</small><b>{{ totalStok }}</b>
      </div>
    </div>

    <!-- BAR PER KATEGORI -->
    <div class="viz">
      <h3>Ringkasan Stok per Kategori</h3>
      <div v-for="k in stokPerKategori" :key="k.kategori" class="bar-row">
        <span class="cat">{{ k.kategori }} ({{ k.total }})</span>
        <div class="bar-bg">
          <div class="bar-fill" :style="{ width: k.persen + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <input v-model="search" placeholder="Cari nama_bahan / kategori..." />
      <button @click="sortAZ = sortAZ === 'AZ' ? 'ZA' : 'AZ'">
        Urut {{ sortAZ }}
      </button>
      <button @click="showForm = !showForm" class="primary">
        {{ showForm ? "Tutup" : "+ Tambah" }}
      </button>
    </div>

    <div v-if="showForm" class="form">
      <input v-model="form.nama_bahan" placeholder="Nama bahan" />
      <select v-model="form.kategori">
        <option>Sayuran</option>
        <option>Daging</option>
        <option>Seafood</option>
        <option>Bumbu</option>
        <option>Produk Olahan</option>
        <option>Beras & Biji</option>
      </select>
      <input
        type="number"
        v-model.number="form.stok"
        placeholder="Stok angka"
      />
      <input v-model="form.satuan" placeholder="kg/liter/pcs/ikat" />
      <button @click="submit" class="primary">
        {{ editId ? "Update" : "Simpan" }}
      </button>
      <button @click="cancelEdit">Batal</button>
    </div>

    <div v-if="sorted.length === 0" class="empty">
      Tidak ada data untuk "{{ search }}"
    </div>

    <div class="table-wrap">
      <table>
        <tr>
          <th>Nama Bahan</th>
          <th>Kategori</th>
          <th>Stok</th>
          <th>Status</th>
          <th>Aksi</th>
        </tr>
        <tr v-for="b in sorted" :key="b.id">
          <td>{{ b.nama_bahan }}</td>
          <td>{{ b.kategori }}</td>
          <td>{{ b.stok }} {{ b.satuan }}</td>
          <td>
            <span class="badge" :class="statusClass(b.stok)">{{
              statusLabel(b.stok)
            }}</span>
          </td>
          <td>
            <button @click="startEdit(b)">Edit</button
            ><button @click="hapus(b.id)">Hapus</button>
          </td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
const API = "http://localhost:8000/api/bahan";

const bahanList = ref([]);
const search = ref("");
const sortAZ = ref("AZ");
const statusFetch = ref("loading");
const errorMsg = ref("");
const showForm = ref(false);
const editId = ref(null);
const form = ref({
  nama_bahan: "",
  kategori: "Sayuran",
  stok: 0,
  satuan: "kg",
});

function statusLabel(s) {
  if (s === 0) return "Stok Habis";
  if (s <= 5) return "Menipis";
  return "Aman";
}
function statusClass(s) {
  if (s === 0) return "habis";
  if (s <= 5) return "menipis";
  return "aman";
}

async function fetchData() {
  statusFetch.value = "loading";
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error("Backend belum jalan");
    const data = await res.json();
    bahanList.value = data;
    statusFetch.value = data.length ? "success" : "empty";
  } catch (e) {
    statusFetch.value = "error";
    errorMsg.value = e.message;
  }
}

const filtered = computed(() => {
  const q = search.value.toLowerCase();
  return bahanList.value.filter(
    (b) =>
      b.nama_bahan.toLowerCase().includes(q) ||
      b.kategori.toLowerCase().includes(q),
  );
});

const sorted = computed(() => {
  return [...filtered.value].sort((a, b) => {
    if (sortAZ.value === "AZ") return a.nama_bahan.localeCompare(b.nama_bahan);
    return b.nama_bahan.localeCompare(a.nama_bahan);
  });
});

const totalBahan = computed(() => bahanList.value.length);
const menipisHabis = computed(
  () => bahanList.value.filter((b) => b.stok <= 5).length,
);
const jumlahKategori = computed(
  () => [...new Set(bahanList.value.map((b) => b.kategori))].length,
);
const totalStok = computed(() =>
  bahanList.value.reduce((s, b) => s + b.stok, 0),
);

const stokPerKategori = computed(() => {
  const m = {};
  bahanList.value.forEach((b) => {
    m[b.kategori] = (m[b.kategori] || 0) + b.stok;
  });
  const max = Math.max(...Object.values(m), 1);
  return Object.entries(m)
    .map(([k, v]) => ({ kategori: k, total: v, persen: (v / max) * 100 }))
    .sort((a, b) => b.total - a.total);
});

async function submit() {
  try {
    const method = editId.value ? "PUT" : "POST";
    const url = editId.value ? `${API}/${editId.value}` : API;
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form.value, stok: Number(form.value.stok) }),
    });
    if (!res.ok) throw new Error("Gagal simpan");
    form.value = { nama_bahan: "", kategori: "Sayuran", stok: 0, satuan: "kg" };
    editId.value = null;
    showForm.value = false;
    await fetchData();
  } catch (e) {
    alert(e.message);
  }
}

async function hapus(id) {
  if (!confirm("Hapus ID " + id + "?")) return;
  await fetch(`${API}/${id}`, { method: "DELETE" });
  await fetchData();
}

function startEdit(b) {
  editId.value = b.id;
  form.value = { ...b };
  showForm.value = true;
}
function cancelEdit() {
  editId.value = null;
  form.value = { nama_bahan: "", kategori: "Sayuran", stok: 0, satuan: "kg" };
  showForm.value = false;
}

onMounted(fetchData);
</script>

<style>
.container {
  max-width: 1100px;
  margin: auto;
  padding: 16px;
  font-family: sans-serif;
}
.sub {
  color: #666;
  font-size: 13px;
  margin-top: 0;
}
.tiles {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 12px 0;
}
.tile {
  border: 1px solid #ddd;
  padding: 12px;
  border-radius: 10px;
  background: #fff;
}
.tile b {
  font-size: 22px;
  display: block;
}
.tile.warn {
  background: #fff3cd;
}
.viz {
  border: 1px solid #eee;
  padding: 12px;
  border-radius: 10px;
  background: #fff;
  margin: 12px 0;
}
.bar-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin: 6px 0;
}
.cat {
  width: 160px;
  font-size: 13px;
}
.bar-bg {
  flex: 1;
  height: 10px;
  background: #eee;
  border-radius: 5px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: #22c55e;
}
.toolbar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 12px 0;
}
.toolbar input {
  flex: 1;
  min-width: 200px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
}
button.primary {
  background: #111;
  color: #fff;
  border-color: #111;
}
.form {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px;
  border: 1px dashed #ccc;
  border-radius: 10px;
  margin: 12px 0;
  background: #fff;
}
.form input,
.form select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
}
.badge.aman {
  background: #dcfce7;
  color: #166534;
}
.badge.menipis {
  background: #fef3c7;
  color: #92400e;
}
.badge.habis {
  background: #fee2e2;
  color: #991b1b;
}
.table-wrap {
  overflow: auto;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 10px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 10px;
  border-bottom: 1px solid #eee;
  text-align: left;
}
.status {
  padding: 10px;
  border-radius: 8px;
  margin: 10px 0;
}
.status.loading {
  background: #e0f2fe;
}
.status.error {
  background: #fee2e2;
  color: #991b1b;
}
.status.success {
  background: #dcfce7;
  color: #166534;
}
.empty {
  padding: 12px;
  border: 1px dashed #ccc;
  text-align: center;
  color: #666;
  margin: 12px 0;
  border-radius: 8px;
}
@media (max-width: 768px) {
  .tiles {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
