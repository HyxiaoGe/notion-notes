# Nginx 复习

_Last updated: 2025-07-28 08:23:54_

---

# Nginx 概述


Nginx（发音为"engine x"）是一个高性能的HTTP和反向代理服务器，也是一个IMAP/POP3/SMTP代理服务器。Nginx由Igor Sysoev于2004年首次公开发布，用于解决C10K问题（即服务器同时处理10,000个客户端连接的问题）。


- **HTTP 服务器**：它可以像 Apache、Tomcat 一样，直接把服务器上的静态文件（比如 HTML、图片、CSS、JS）返回给用户的浏览器。

- **反向代理服务器**：这是它最重要、最常见的角色。它作为后端服务（比如你的 Java、Go、Python 应用）的“门户”，接收所有用户的请求，然后再把请求转发给后端的具体服务去处理。

# **Nginx 核心特性总结**


**1. 高并发、高性能 (High Concurrency & High Performance)**


- 这是 Nginx 最广为人知的标签。它能以极低的内存和 CPU 资源消耗，轻松维持数万甚至数十万级别的并发连接。

- **核心原因**：它从根本上解决了 **C10K 问题**，是为高并发场景而生的。

**2. 事件驱动的异步非阻塞架构 (Event-Driven, Asynchronous Non-Blocking)**


- 这是实现“高并发、高性能”的**技术基石**。

- **工作方式**：Nginx 在处理网络连接和请求时，不会因为某个任务（如等待客户端发送数据或等待后端返回结果）而“傻等”（阻塞）。它会注册一个“事件”，然后立即去处理其他任务。当等待的任务完成后，它会接收到通知，再回来处理后续步骤。

- **结果**：用极少数的工作进程就能“应付”海量的并发任务，大大节省了系统资源。

**3. 强大的代理与网关层 (Robust Proxy and Gateway Layer)**


- Nginx 不仅仅是简单的请求转发，它是一个功能丰富的**应用网关**。

- **体现在**：
    - **反向代理**：隐藏和保护后端服务。
    - **负载均衡**：将请求压力分摊到多个后端服务器。
    - **安全屏障**：可配置访问控制、速率限制，抵御部分网络攻击。
    - **性能优化**：能执行 SSL 加密卸载、内容缓存、Gzip 压缩等，为后端减负。

**4. 明确的职责分离 (Clear Separation of Concerns)**


- Nginx 完美地将 **网络连接管理** 与 **业务逻辑处理** 这两个职责分离开。

- **职责划分**：
    - **Nginx**：专心处理所有与客户端之间的**网络 I/O**，无论连接是快是慢。
    - **后端服务**：从繁杂的网络问题中解脱出来，专心处理**业务逻辑**和**数据 I/O**（如数据库读写）。

- **结果**：架构更清晰，使得各个部分可以独立优化和扩展。

**5. 忠实的“问题报告者” (Faithful Problem Reporter)**


- 当后端服务出现问题时，Nginx 不会隐藏问题，而是会明确地向客户端报告。

- **典型例子**：
    - `**502 Bad Gateway**`：后端服务不可达或已崩溃。
    - `**504 Gateway Timeout**`：后端服务处理请求太慢，超时了。

# Nginx 的常见应用场景


- **静态资源服务器：**高效地提供静态文件如HTML、CSS、JavaScript、图片等。

- **反向代理服务器：**接收客户端请求并转发到后端服务器。

- **负载均衡器：**分发请求到多个后端服务器，提高系统整体性能和可靠性。

- **HTTP缓存：**缓存静态内容，减少后端服务器的负载。

- **API网关：**作为API请求的入口点，处理路由、认证、限流等功能。

# 与其他Web服务器的比较


相比Apache等传统Web服务器，Nginx在处理高并发连接方面表现更佳，资源消耗更低。与此同时，Nginx的配置相对简单，学习曲线较平缓。


# Nginx 的工作模型


Nginx 的高性能秘密，就藏在它独特的工作模型里。这个模型可以拆分成两个层面来理解：


- **宏观的进程架构**：它是如何组织自己的进程的？(Master-Worker 模型)

- **微观的工作方式**：每个进程是如何处理海量连接的？(I/O 多路复用)

# **Master-Worker 多进程模型**


当你在服务器上启动 Nginx 后，用 `ps -ef | grep nginx` 命令查看，通常会看到至少两个进程：一个 **Master 进程**和一个或多个 **Worker 进程**。


**1. Master 进程 (主进程 / “管理者”)**


Master 进程的角色是“领导”和“管理员”，它**不直接处理任何用户的网络请求**。它的主要工作是：


- **读取并验证配置**：启动时，它会读取 `nginx.conf` 配置文件，检查语法是否正确。

- **创建和绑定端口**：它会负责监听配置文件中指定的端口（如 80, 443）。

- **管理 Worker 进程**：
    - 根据配置（`worker_processes` 指令）或者服务器的 CPU核心数，创建指定数量的 Worker 进程。
    - 监控 Worker 进程的健康状态，如果某个 Worker 意外死掉了，Master 会立刻重新拉起一个新的。
    - 接收来自管理员的控制信号，实现 Nginx 的平滑升级、优雅重启、停止服务等。例如，当你执行 `nginx -s reload` 来热加载配置时，就是 Master 进程在工作。

**简单说，Master 进程就像一个“工头”，负责准备工作环境、招募并管理工人，但它自己不上一线干活。**


**2. Worker 进程 (工作进程 / “工人”)**


Worker 进程才是真正处理用户请求的“一线员工”。


- **处理连接和请求**：所有的用户连接和请求，都是由 Worker 进程来接收、处理和响应的。

- **相互独立**：每个 Worker 进程都是一个独立的、单线程的进程。它们之间几乎没有共享数据，处理请求时互不干扰，这保证了高可靠性，一个 Worker 的崩溃不会影响其他 Worker。

- **共享监听端口**：所有 Worker 进程都会共同监听由 Master 进程打开的端口。当一个新连接到来时，所有 Worker 会通过操作系统的机制（如 `accept_mutex` 锁）来“争抢”这个连接，最终只有一个 Worker 会成功接收并处理它。

**这个 “一个管理者 + 多个高效工人” 的模型有几个巨大的好处：**


- **稳定性**：Master 作为守护进程，保证了 Worker 的稳定运行。Worker 之间相互隔离，一个出问题不影响全局。

- **高可用性**：可以在不停止服务的情况下，通过向 Master 发送信号来平滑地升级程序、更新配置。

- **利用多核**：可以配置与 CPU 核心数相等的 Worker 进程数，充分利用多核 CPU 的处理能力。

**每个 Worker 进程都是单线程的，它凭什么能独自处理成千上万的并发连接呢？**


#  I/O 多路复用 (以 epoll 为例)



Worker 进程高效的秘密武器，就是 **I/O 多路复用 (I/O Multiplexing)**。在 Linux 系统上，它具体的技术实现就是 **epoll，**应用程序可以通过调用 `epoll_create`, `epoll_ctl`, `epoll_wait` 这几个函数，来委托内核去帮它高效地管理大量的网络连接。


1. 一个 Worker 进程把自己关心的所有连接（Socket）都注册到 `epoll` 系统中。

2. 然后 Worker 进程就休眠了，调用 `epoll_wait()` 等待事件发生，几乎不占 CPU。

3. 当某个连接上有数据传来、或可以发送数据时（即 I/O 事件就绪），操作系统会通知 Worker 进程，并把所有**已就绪**的连接列表告诉它。

4. Worker 进程被唤醒，拿到这个“就绪列表”，然后依次处理这些连接上的请求。处理完后，继续回去“睡觉”，等待下一次的事件通知。

# **总结：**


Nginx 的高性能模型 = **Master-Worker 多进程架构** (充分利用多核、稳定可靠) + **I/O 多路复用 **`**epoll**` (单个 Worker 进程高效处理海量连接的核心技术)。


# Nginx 的配置与核心指令


# **Nginx 的安装与目录结构**


通常，我们通过包管理器（如 `yum` 或 `apt-get`）安装 Nginx。


记住以下几个核心位置至关重要：


- **主配置文件**: `/etc/nginx/nginx.conf`
    - 这是 Nginx 的“大脑”，几乎所有的配置都从这里开始。

- **可拆分的配置目录**: `/etc/nginx/conf.d/`
    - 在实践中，我们很少把所有配置都写在 `nginx.conf` 这一个文件里。通常，`nginx.conf` 会通过 `include /etc/nginx/conf.d/*.conf;` 这样的指令，把这个目录下的所有 `.conf` 文件都加载进来。
    - **最佳实践**：每为一个网站或一个服务做代理，就在 `conf.d` 目录下新建一个独立的配置文件（如 `my_app.conf`）。这让配置管理变得非常清晰。

- **日志文件目录**: `/var/log/nginx/`
    - `**access.log**`: 访问日志。记录了每一个请求的详细信息（谁访问的、访问了什么、何时访问、响应状态等）。是排查业务问题和做数据分析的基础。
    - `**error.log**`: 错误日志。记录了 Nginx 启动、运行过程中的所有错误信息。**当 Nginx 启动失败或者出现 5xx 错误时，第一时间就应该来这里找线索。**

- **默认网站根目录**: `/usr/share/nginx/html/`
    - 当你安装完 Nginx 第一次启动，在浏览器里访问服务器 IP，看到的那个“Welcome to Nginx!”页面，就是存放在这个目录下的 `index.html`。

# **Nginx 的基本控制命令**


我们通常使用 `nginx` 这个可执行文件（或者通过 `systemctl`），配合不同的参数来控制它。


- **测试配置**：`nginx -t`
    - **极其重要！** 在你修改了任何 `.conf` 配置文件后，**永远不要直接重启 Nginx**。先执行 `nginx -t`，它会检查所有配置文件的语法。如果没问题，它会提示 `syntax is ok` 和 `test is successful`。这能避免因为一个小小的语法错误（比如少个分号）导致整个网站宕机。

- **启动 Nginx**：`nginx` 或 `systemctl start nginx`
    - 直接执行 `nginx` 命令（或使用 `systemctl`）。

- **停止 Nginx**：
    - `nginx -s stop`：快速停止，不管当前有无正在处理的请求，直接“一刀切”。
    - `nginx -s quit`：优雅停止 (graceful stop)，会等待当前所有正在处理的请求完成后，再关闭进程。

# **Nginx 核心指令解析**


```json
#================ 全局块 (Global Block) ================
# 这部分没有花括号，是最高层级的指令。
user  nginx;
worker_processes  auto; # 通常设置为 auto 或 CPU 核心数
error_log /var/log/nginx/error.log warn;
#====================================================


#================ events 块 ================
# 配置与网络连接相关的参数
events {
    worker_connections  1024; # 每个 worker 进程能处理的最大连接数
    use epoll; # 在 Linux 上使用 epoll 模型，性能最高
}
#===========================================


#================ http 块 ================
# 这是配置 Web 服务和代理功能最核心的块
http {
    # --- http 全局配置 ---
    # 定义了可以在 http 块下所有 server 块中使用的公共配置
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    access_log  /var/log/nginx/access.log  main;
    sendfile        on;
    keepalive_timeout  65;


    # --- server 块 (定义一个虚拟主机) ---
    server {
        listen       80; # 监听 80 端口
        server_name  www.example.com; # 对应的域名

        # --- location 块 (定义请求路由规则) ---
        location / {
            root   /usr/share/nginx/html; # 网站根目录
            index  index.html index.htm;   # 默认首页文件
        }

        location /api/ {
            # 这里的规则会匹配所有 "www.example.com/api/..." 的请求
            # 比如，可以把请求转发给后端服务
            proxy_pass http://backend_server_address;
        }
    }

    # --- 可以定义第二个 server 块 ---
    server {
        listen 80;
        server_name another.example.com;
        # ... 针对 another.example.com 的配置 ...
    }
}
#===========================================
```


**全局块 (Global Block)**


- `*user**`
指定 Nginx 的 Worker 进程以哪个用户和用户组的身份运行。出于安全考虑，通常会指定为一个权限较低的专用用户（如 `nginx` 或 `www-data`）。

- `*worker_processes**`
设置 Worker 进程的数量。这是性能调优的关键，最佳实践是设置为 `auto`，Nginx 会自动检测服务器的 CPU 核心数并以此作为 Worker 数量。

- `*error_log**`
定义全局的错误日志文件路径和记录级别。当 Nginx 遇到问题时（如配置错误、启动失败），这里是寻找线索的首要地点。

- `*pid**`
指定存放 Master 进程 ID 的文件路径。这个文件主要用于脚本自动化控制 Nginx。

`**events**`** 块**


- `*worker_connections**`
设置**每一个** Worker 进程能够同时处理的最大连接数。这是 Nginx 并发能力的核心指标。服务器的总并发能力理论上等于 `worker_processes * worker_connections`。

- `*use**`
指定 Nginx 使用的 I/O 多路复用模型。如我们所讨论的，在 Linux 上 Nginx 会自动选择最高效的 `epoll`，所以此项一般无需配置。

`**http**`** 块**


- `*include**`
用于引入其他的配置文件，是保持主配置文件 `nginx.conf` 简洁的最佳实践。`include /etc/nginx/conf.d/*.conf;` 就是一个典型的例子。`mime.types` 这个文件里定义了文件扩展名和MIME类型（Content-Type）之间的对应关系。比如，它里面有这样的内容：`text/html html;`、`image/jpeg jpg jpeg;`。浏览器需要根据服务器返回的 `Content-Type` 头来决定如何展示一个文件（是当成网页渲染，还是当成图片显示）。

- `*access_log**`
设置访问日志的存放路径和使用的格式。可以设置 `off` 来关闭日志记录。

- `*log_format**`
自定义访问日志的格式。可以添加更多变量（如 `$request_time`, `$upstream_response_time`）来记录请求耗时等信息，对于性能分析非常有用。

- `*sendfile**`
一个性能优化指令。设置为 `on` 会启用操作系统高效的文件传输模式（零拷贝），可以让 Nginx 在传输静态文件时更快、更节省资源。

- `*keepalive_timeout**`
设置 HTTP 长连接的超时时间。合理的设置可以减少客户端与服务器之间频繁建立和断开 TCP 连接的开销，提升性能。

- `*client_max_body_size**`
限制客户端请求体（Request Body）的最大尺寸。当用户需要上传文件时，如果文件大小超过这个值，Nginx 会返回 `413 Request Entity Too Large` 错误。这是控制资源滥用的重要指令。

`**server**`** 块**


- `*listen**`
指定虚拟主机监听的端口号。可以附加 `ssl` 参数来表示此端口用于 HTTPS 通信。例如：`listen 443 ssl;`。

- `*server_name**`
指定虚拟主机的域名。Nginx 通过请求头中的 `Host` 字段来匹配对应的 `server_name`，从而决定由哪个 `server` 块来处理该请求。这是实现虚拟主机的关键。

`**location**`** 块**


这是 Nginx 配置中最核心、最灵活的部分，决定了如何处理具体的请求 URI。


- `*root**`
指定静态文件的根目录。当请求匹配到这个 `location` 时，Nginx 会将请求的 URI 拼接到 `root` 指定的路径后，去硬盘上寻找对应的文件。
```json
server {
    listen 80;
    server_name example.com;

    # 示例: 访问 http://example.com/images/logo.png
    location /images/ {
        root /var/www/app; 
        # Nginx 寻找的物理路径是：
        # /var/www/app   +   /images/logo.png
        # 结果: /var/www/app/images/logo.png
    }
}
```


- `*index**`
当请求的 URI 是一个目录时，指定默认去查找的文件名。例如，访问 `http://example.com/` 时，Nginx 会依次尝试查找 `root` 目录下的 `index.html` 和 `index.htm` 文件。
    - **访问 **`**http://example.com/**`：Nginx 会先寻找 `/var/www/app/index.html`，如果找不到，再寻找 `/var/www/app/index.php`。
```json
location / {
    root /var/www/app;
    index index.html index.php; # 优先找 index.html, 找不到再找 index.php
}
```


- `*proxy_pass**`**反向代理的核心指令**。它指定了要将请求转发到的后端服务器地址。地址可以是 IP:Port、域名，或者是一个通过 `upstream` 块定义的服务器组。
    - **访问 **`**http://example.com/api/users**`：
    - **注意**：`proxy_pass` 后面地址的 `/` 非常关键：
        - 带 `/` (`http://.../`)：表示将原始 URI 中匹配 `location` 的部分（`/api/`）去掉后再拼接；Nginx 会将请求转发到 `http://127.0.0.1:8080/users`。
        - 不带 `/` (`http://...`)：表示将原始 URI 原封不动地拼接到后面；Nginx 会将请求转发到 `http://127.0.0.1:8080/api/users`。
```json
location /api/ {
    # 将所有 /api/ 开头的请求转发给运行在 8080 端口的后端应用
    proxy_pass http://127.0.0.1:8080/;
}
```

