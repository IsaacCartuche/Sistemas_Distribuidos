package org.ejemplo;

import io.javalin.Javalin;
import io.javalin.websocket.WsContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class ServidorSockets {

    // Estado global
    private static int faseActual = 1;
    private static WsContext presentador = null;
    // Map seguro para hilos: guarda el ID del cliente y su conexión
    private static final Map<String, WsContext> clientesActivos = new ConcurrentHashMap<>();
    private static final ObjectMapper mapper = new ObjectMapper();

    public static void main(String[] args) {
        Javalin app = Javalin.create(config -> {
            config.staticFiles.add("/public");
        }).start(8080);

        // --- WEBSOCKET PARA EL PROYECTOR ---
        app.ws("/ws/proyector", ws -> {
            ws.onConnect(ctx -> {
                presentador = ctx;
                System.out.println("Proyector conectado.");
            });

            ws.onMessage(ctx -> {
                JsonNode mensaje = mapper.readTree(ctx.message());
                if (mensaje.has("accion") && mensaje.get("accion").asText().equals("cambiar_fase")) {
                    faseActual = mensaje.get("fase").asInt();
                    notificarClientesFase();
                }
            });

            ws.onClose(ctx -> presentador = null);
        });

        // --- WEBSOCKET PARA EL PÚBLICO (CLIENTES) ---
        app.ws("/ws/cliente", ws -> {
            ws.onConnect(ctx -> {
                String clientId = UUID.randomUUID().toString().substring(0, 8);
                // Guardamos el ID en la sesión del cliente
                ctx.attribute("id", clientId);
                clientesActivos.put(clientId, ctx);
                
                // Le enviamos la fase actual apenas se conecta
                ObjectNode node = mapper.createObjectNode();
                node.put("tipo", "cambio_fase");
                node.put("fase", faseActual);
                ctx.send(node.toString());

                // Avisar al proyector que hay un nuevo cliente
                if (presentador != null) {
                    ObjectNode aviso = mapper.createObjectNode();
                    aviso.put("tipo", "nuevo_cliente");
                    aviso.put("id", clientId);
                    presentador.send(aviso.toString());
                }
            });

            ws.onMessage(ctx -> {
                JsonNode mensaje = mapper.readTree(ctx.message());
                String clientId = ctx.attribute("id");

                // Fase 3: Transmisión de datos
                if (faseActual == 3 && mensaje.has("accion") && mensaje.get("accion").asText().equals("enviar_datos")) {
                    String payload = mensaje.has("payload") ? mensaje.get("payload").asText() : "Ping";
                    
                    // Reenviar al proyector para la animación
                    if (presentador != null) {
                        ObjectNode datoRecibido = mapper.createObjectNode();
                        datoRecibido.put("tipo", "dato_recibido");
                        datoRecibido.put("id_cliente", clientId);
                        datoRecibido.put("payload", payload);
                        presentador.send(datoRecibido.toString());
                    }
                    
                    // Responder al cliente
                    ObjectNode respuesta = mapper.createObjectNode();
                    respuesta.put("tipo", "respuesta_servidor");
                    respuesta.put("payload", "Pong!");
                    ctx.send(respuesta.toString());
                }
            });

            ws.onClose(ctx -> {
                String clientId = ctx.attribute("id");
                if (clientId != null) {
                    clientesActivos.remove(clientId);
                    if (presentador != null) {
                        ObjectNode aviso = mapper.createObjectNode();
                        aviso.put("tipo", "cliente_desconectado");
                        aviso.put("id", clientId);
                        presentador.send(aviso.toString());
                    }
                }
            });
        });
    }

    // Método auxiliar para avisar a todos los teléfonos del cambio de fase
    private static void notificarClientesFase() {
        ObjectNode node = mapper.createObjectNode();
        node.put("tipo", "cambio_fase");
        node.put("fase", faseActual);
        String mensajeJson = node.toString();

        clientesActivos.values().forEach(ctx -> {
            if (ctx.session.isOpen()) {
                ctx.send(mensajeJson);
            }
        });
    }
}