import React, { useEffect, useState } from "react";
import "../chat.css";
// Conection to backend flask
const API_URL = import.meta.env.VITE_REACT_APP_API;

function Chat() {
  const [user, setUser] = useState("");
  const [id, setId] = useState("");
  const [token, setToken] = useState("");

  const [contacts, setContacts] = useState([]);
  const [chat, setChat] = useState([]);
  const [input_id_contact, setInput_id_contact] = useState("");
  const [contact_user, setContact_user] = useState("");
  const [content, setContent] = useState("");
  const [id_other, setId_other] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const storedId = localStorage.getItem("id");
    const storedToken = localStorage.getItem("token");

    if (!storedUser && !storedId) {
      // Si no se encuentra el nombre de usuario en el almacenamiento local, redirigir al inicio de sesión
      window.location.replace("/");
    } else {
      // Si se encuentra el nombre de usuario, establecer el estado del usuario
      setUser(storedUser);
      setId(storedId);
      setToken(storedToken);
    }
  }, []);

  //get chatnames

  const getContacts = async (id) => {
    const response = await fetch(`${API_URL}/tableid/${id}`);
    const data = await response.json();
    setContacts(data);
  };

  useEffect(() => {
    getContacts(id);
  });

  // Function to handle button click
  const handleButtonClick = async (id, id_contact) => {
    try {
      const response = await fetch(`${API_URL}/tablechat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id,
          id_contact,
        }),
      });

      // Aquí puedes manejar la respuesta, si es necesario
      // Por ejemplo, verificar el estado de la respuesta y actuar en consecuencia
      if (response.ok) {
        console.log("La solicitud se completó exitosamente.");
      } else {
        console.log("ya esta  creado.");
      }

      Showchat(id, id_contact);
    } catch (error) {
      console.error("Error en la solicitud:", error);
    }
  };

  const Showchat = async (id, id_contact) => {
    const response = await fetch(`${API_URL}/tablechat/${id}/${id_contact}`);
    const data = await response.json();
    setChat(data);
    setId_other(id_contact);

    /* useEffect(() => {
      Showchat(id, id_contact);
    } , ); */
  };

  useEffect(() => {
    const intervalId = setInterval(() => {
      Showchat(id, id_other);
    }, 2000); // 2000 milisegundos = 2 segundos

    // Se debe limpiar el intervalo cuando el componente se desmonte para evitar fugas de memoria.
    return () => clearInterval(intervalId);
  }, [id, id_other]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input_id_contact === "" || contact_user === "") {
      window.alert("Please fill all fields");
      return;
    }
    try {
      const response = await fetch(`${API_URL}/tableid/${id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_contact: input_id_contact,
          user: contact_user,
        }),
      });

      // Aquí puedes manejar la respuesta, si es necesario
      // Por ejemplo, verificar el estado de la respuesta y actuar en consecuencia
      if (response.ok) {
        console.log("La solicitud se completó exitosamente.");
      } else {
        console.log("Hubo un error al procesar la solicitud.");
      }

      setInput_id_contact("");
      setContact_user("");
    } catch (error) {
      console.error("Error en la solicitud:", error);
    }
  };

  const sendMessage = async (id_other) => {
    console.log(id_other);
    const response = await fetch(`${API_URL}/tablechat/${id}/${id_other}`, {
      method: "POST",
      body: JSON.stringify({
        content,
        sender_id: id,
        receiver_id: id_other,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });
    setContent("");
    Showchat(id, id_other);

    if (response.ok) {
      console.log("enviado exitosamente.");
    } else {
      console.log("no se envio :( ");
    }
  };

  return (
    <div className="dark-theme">
      <h1>Chat</h1>
      <div className="flex">
        <div className="column">
          <div className="column-create">
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                onChange={(e) => setInput_id_contact(e.target.value)}
                value={input_id_contact}
                placeholder="Add id of contact"
                autoFocus
                className="input-createname"
              />

              <br />
              <br />
              <input
                type="text"
                onChange={(e) => setContact_user(e.target.value)}
                value={contact_user}
                placeholder="Add name of contact"
                autoFocus
                className="input-createname"
              />

              <button type="submit" className="btn-create-name">
                Create Contact
              </button>
            </form>
          </div>

          <div className="column-chats">
            {contacts.map((contact) => (
              <div key={contact.id}>
                <button
                  onClick={() => handleButtonClick(id, contact.id_contact)}
                  className="btn-chats"
                >
                  {contact.user}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div>

        <div className="view-chat">
  {chat.map((chatItem) => (
    <div
      key={chatItem.id}
      className={chatItem.receiver_id === id_other ? "sent-message" : "received-message "}
    >
      <div>
        <p className="chat">{chatItem.content}</p>
      </div>
    </div>
  ))}
</div>


          <div className="input">
            <textarea
              onChange={(e) => setContent(e.target.value)}
              value={content}
              placeholder="Add a message"
              autoFocus
              className="input-user"
            />

            <button
              onClick={() => sendMessage(id_other)}
              className="btn-send"
              id="send-button"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
