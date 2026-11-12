import {useState, useEffect} from "react";

const API = "http://localhost:8000";

function App() {
  const [packages, setPackages] = useState([]);
  const [batches, setBatches] = useState([]);
  const [reload, setReload] = useState(0);
  const [message, setMessage] = useState("");

  const [filters, setFilters] = useState({destination: "", status: "", arrival_date: ""});
  const [batchFilters, setBatchFilters] = useState({destination: "", vehicle_number: "", dispatch_status: ""});

  const [newPackage, setNewPackage] = useState({name: "", destination: "", weight: ""});
  const [editPackage, setEditPackage] = useState({id: "", name: "", destination: "", weight: ""});
  const [newBatch, setNewBatch] = useState({destination: "", vehicle_number: ""});

  const [lookupId, setLookupId] = useState("");
  const [foundPackage, setFoundPackage] = useState(null);

  // E5 loads packages with whatever filters are filled in
  useEffect(() => {
    async function loadPackages() {
      let query = "";
      if (filters.destination !== "") {
        query = query + `destination=${filters.destination}&`;
      }
      if (filters.status !== "") {
        query = query + `status=${filters.status}&`;
      }
      if (filters.arrival_date !== "") {
        query = query + `arrival_date=${filters.arrival_date}&`;
      }

      const res = await fetch(`${API}/packages?${query}`);
      const data = await res.json();

      if (data.detail) {
        setPackages([]);
      } else {
        setPackages(data);
      }
    }
    loadPackages();
  }, [reload]);

  // E6 and E7 load dispatch batches, filters filled in means E6, no filters means E7
  useEffect(() => {
    async function loadBatches() {
      let query = "";
      if (batchFilters.destination !== "") {
        query = query + `destination=${batchFilters.destination}&`;
      }
      if (batchFilters.vehicle_number !== "") {
        query = query + `vehicle_number=${batchFilters.vehicle_number}&`;
      }
      if (batchFilters.dispatch_status !== "") {
        query = query + `dispatch_status=${batchFilters.dispatch_status}&`;
      }

      let url = `${API}/warehouse/summary`;
      if (query !== "") {
        url = `${API}/dispatch-batches?${query}`;
      }

      const res = await fetch(url);
      const data = await res.json();

      if (data.detail) {
        setBatches([]);
      } else {
        setBatches(data);
      }
    }
    loadBatches();
  }, [reload]);

  // shared helper for the POST, PATCH and DELETE calls
  async function send(url, method) {
    const res = await fetch(`${API}${url}`, {method: method});
    const data = await res.json();

    if (data.detail) {
      setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
    } else {
      setMessage(data.message);
    }
    setReload(reload + 1);
  }

  // E1 registers a package
  function registerPackage() {
    send(`/packages?name=${newPackage.name}&destination=${newPackage.destination}&weight=${newPackage.weight}`, "POST");
  }

  // E2 gets one package by id
  async function findPackage() {
    const res = await fetch(`${API}/packages/${lookupId}`);
    const data = await res.json();

    if (data.detail) {
      setFoundPackage(null);
      setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
    } else {
      setFoundPackage(data);
      setMessage("");
    }
  }

  // E3 updates a package, only the filled in fields are sent
  function updatePackage() {
    let query = "";
    if (editPackage.name !== "") {
      query = query + `name=${editPackage.name}&`;
    }
    if (editPackage.destination !== "") {
      query = query + `destination=${editPackage.destination}&`;
    }
    if (editPackage.weight !== "") {
      query = query + `weight=${editPackage.weight}&`;
    }

    send(`/packages/${editPackage.id}?${query}`, "PATCH");
  }

  // E4 deletes a package
  function deletePackage(id) {
    send(`/packages/${id}`, "DELETE");
  }

  // E8 creates a dispatch batch
  function createBatch() {
    send(`/dispatch-batches?destination=${newBatch.destination}&vehicle_number=${newBatch.vehicle_number}`, "POST");
  }

  return (
    <>
    </>
  );
}

export default App;