// module.exports = {
//   apps: [
//     {
//       name: "diaba-test-api", 
//       script: "/home/ubuntu/testDiaba/api/envdiaba/bin/uvicorn",
//       // We are now running the ASGI application on port 4001
//       args: "diaba.asgi:application --host 0.0.0.0 --port 4001",
//       cwd: "/home/ubuntu/testDiaba/api/diaba",
//       interpreter: "none",
//       watch: false,
//       autorestart: true,
//       max_restarts: 10,
//       max_memory_restart: "1G",
//       env: {
//         DJANGO_SETTINGS_MODULE: "diaba.settings",
//         PYTHONUNBUFFERED: "1",
//       },
//       out_file: "/home/ubuntu/logs/test-diaba-unified-out.log",
//       error_file: "/home/ubuntu/logs/test-diaba-unified-error.log",
//       log_file: "/home/ubuntu/logs/test-diaba-unified-combined.log",
//       time: true,
//     },
//   ],
// };


module.exports = {
  apps: [
    {
      name: "diaba-test-api",

      script: "/home/ubuntu/testDiaba/api/envdiaba/bin/uvicorn",
      args: "diaba.asgi:application --host 0.0.0.0 --port 4001",

      cwd: "/home/ubuntu/testDiaba/api/diaba",

      interpreter: "none",

      watch: false,
      autorestart: true,

      // Stop PM2 from endlessly restarting a broken process
      max_restarts: 10,
      min_uptime: "10s",

      max_memory_restart: "1G",

      env: {
        DJANGO_SETTINGS_MODULE: "diaba.settings",
        PYTHONUNBUFFERED: "1",
        PATH: "/home/ubuntu/testDiaba/api/envdiaba/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      },

      out_file: "/home/ubuntu/logs/test-diaba-unified-out.log",
      error_file: "/home/ubuntu/logs/test-diaba-unified-error.log",
      log_file: "/home/ubuntu/logs/test-diaba-unified-combined.log",

      time: true,
    },
  ],
};