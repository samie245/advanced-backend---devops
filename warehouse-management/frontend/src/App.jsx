import { useState, useEffect } from "react";

const API = "http://localhost:8000";

// builds "?a=1&b=2" and skips empty fields
function buildQuery(fields) {
  const parts = [];
  for (const key in fields) {
    if (fields[key] !== "") {
      parts.push(`${key}=${encodeURIComponent(fields[key])}`);
    }
  }
  return parts.length > 0 ? `?${parts.join("&")}` : "";
}

function App() {
  const [packages, setPackages] = useState([]);
  const [batches, setBatches] = useState([]);
  const [reload, setReload] = useState(0);
  const [message, setMessage] = useState("");

  const [filters, setFilters] = useState({ destination: "", status: "", arrival_date: "" });
  const [batchFilters, setBatchFilters] = useState({ destination: "", vehicle_number: "", dispatch_status: "" });

  const [newPackage, setNewPackage] = useState({ name: "", destination: "", weight: "" });
  const [editPackage, setEditPackage] = useState({ id: "", name: "", destination: "", weight: "" });
  const [newBatch, setNewBatch] = useState({ destination: "", vehicle_number: "" });

  const [lookupId, setLookupId] = useState("");
  const [foundPackage, setFoundPackage] = useState(null);

  // E5 - load packages (with whatever filters are filled in)
  useEffect(() => {
    async function loadPackages() {
      const res = await fetch(`${API}/packages${buildQuery(filters)}`);
      const data = await res.json();

      if (res.ok) {
        setPackages(data);
      } else {
        setPackages([]);
      }
    }
    loadPackages();
  }, [reload]);

  // E6 / E7 - load dispatch batches (filtered -> E6, unfiltered -> E7)
  useEffect(() => {
    async function loadBatches() {
      const query = buildQuery(batchFilters);
      const url = query === "" ? `${API}/warehouse/summary` : `${API}/dispatch-batches${query}`;
      const res = await fetch(url);
      const data = await res.json();

      if (res.ok) {
        setBatches(data);
      } else {
        setBatches([]);
      }
    }
    loadBatches();
  }, [reload]);

  // shared helper for the POST / PATCH / DELETE calls
  async function send(url, method) {
    const res = await fetch(`${API}${url}`, { method: method });
    const data = await res.json();

    if (res.ok) {
      setMessage(data.message);
    } else {
      setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
    }
    setReload(reload + 1);
  }

  // E2 - get one package by id
  async function findPackage() {
    const res = await fetch(`${API}/packages/${lookupId}`);
    const data = await res.json();

    if (res.ok) {
      setFoundPackage(data);
      setMessage("");
    } else {
      setFoundPackage(null);
      setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
    }
  }

  return (
    <>
    </>
  );
}

export default App;