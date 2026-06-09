import { useEffect, useState } from "react";

export default function Galeria() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/experiencias")
      .then(res => res.json())
      .then(res => setData(res))
      .catch(err => console.error(err));
  }, []);

  return (
    <div>
      <h1>Galería</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "20px" }}>
        {data.map((item) => (
          <div key={item.id} style={{ border: "1px solid #ccc", padding: "10px" }}>
            
            <img
              src={`http://127.0.0.1:5000/static/uploads/${item.image}`}
              alt=""
              style={{ width: "100%" }}
            />

            <h3>{item.title}</h3>
            <p>{item.persona}</p>
            <p>{item.description}</p>

            <a href={`/experiencia/${item.id}`}>
              Ver experiencia
            </a>

          </div>
        ))}
      </div>
    </div>
  );
}