# Usa a imagem oficial do Nginx
FROM nginx:alpine

# Apaga a configuração padrão
RUN rm -rf /usr/share/nginx/html/*

# Copia o conteúdo da pasta static/ para o Nginx
COPY static/ /usr/share/nginx/html/

# Expõe a porta 80
EXPOSE 80

# Inicializa o Nginx
CMD ["nginx", "-g", "daemon off;"]
