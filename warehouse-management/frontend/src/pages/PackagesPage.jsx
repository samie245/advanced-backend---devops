import {useState, useEffect} from "react";


function PackagesPage({token}) {
    const [packages, setPackages] = useState([]);
    const [message, setMessage] = useState("");

    // E5 loads all the packages
    useEffect(() => {
        async function loadPackages() {
            const res = await fetch("http://localhost:8001/packages", {headers: {token: token}});
            const data = await res.json();

            if (data.detail) {
                setPackages([]);
                setMessage(typeof data.detail === "string" ? data.detail : "Invalid input");
            } else {
                setPackages(data);
                setMessage("");
            }
        }
        loadPackages();
    }, [token]);

    if (token === "") return <p>Please log in first.</p>;

    return (
        <>
        <p>Loaded {packages.length} packages.</p>
        <p>{message}</p>
        <ul>
            {packages.map((pkg) => (
                <li key={pkg.package_id}>
                    <h3>{pkg.name}</h3>
                    <p>ID: {pkg.package_id}</p>
                    <p>Destination: {pkg.destination}</p>
                    <p>Weight: {pkg.weight}</p>
                    <p>Arrival: {pkg.arrival_date}</p>
                    <p>Status: {pkg.status}</p>
                </li>
            ))}
        </ul>
        </>
    );
}


export default PackagesPage