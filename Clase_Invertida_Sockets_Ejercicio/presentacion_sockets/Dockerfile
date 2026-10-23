# Imagen base oficial con Maven y JDK 17
FROM maven:3.9-eclipse-temurin-17

# Definir el directorio de trabajo interno
WORKDIR /app

# Copiar el pom.xml primero para aprovechar el caché de Docker
# Esto evita volver a descargar dependencias de Internet si solo modificas el código Java o HTML
COPY pom.xml .
RUN mvn dependency:go-offline

# Copiar el resto del código fuente (Java y HTML)
COPY src ./src

# Exponer el puerto donde corre Javalin
EXPOSE 8080

# Compilar y ejecutar la clase principal al arrancar el contenedor
CMD ["mvn", "compile", "exec:java", "-Dexec.mainClass=org.ejemplo.ServidorSockets"]