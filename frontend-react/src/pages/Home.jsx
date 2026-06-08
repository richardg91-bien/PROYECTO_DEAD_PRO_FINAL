import { useEffect, useState } from "react";
import api from "../services/api";

function Home() {
  const [mensaje, setMensaje] = useState("Conectando...");

  useEffect(() => {
    api.get("/api/test")
      .then((res) => setMensaje(res.data.mensaje))
      .catch((err) => {
        console.error(err);
        setMensaje("Error conectando con Flask");
      });
  }, []);

  return (
    <div>
      <h1>Proyecto Dead</h1>
      <p>{mensaje}</p>
    </div>
  );
}

export default Home;