import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import path from "path";
import { viteStaticCopy } from "vite-plugin-static-copy";

export default defineConfig({
    plugins: [
        react(),
        VitePWA({
            registerType: "autoUpdate",
            includeAssets: ["favicon.svg", "favicon.ico", "robots.txt", "apple-touch-icon.png"],
            manifest: {
                name: "Personal Assistant",
                short_name: "Vasi",
                description: "A Voice activated smart interface that helps you with your daily tasks.",
                theme_color: "#000000",
                background_color: "#000000",
                icons: [
                    {
                        src: "./assets/pwa-192x192.png",
                        sizes: "192x192",
                        type: "image/png"
                    },
                    {
                        src: "./assets/pwa-512x512.png",
                        sizes: "512x512",
                        type: "image/png"
                    }
                ]
            },
            workbox: {
                navigateFallback: "/index.html",
                navigateFallbackDenylist: [/\/\.auth\/.*/],
                skipWaiting: true,
                clientsClaim: true
            }
        }),
        viteStaticCopy({
            targets: [
                { src: "src/assets/pwa-192x192.png", dest: "../../backend/static/assets" },
                { src: "src/assets/pwa-512x512.png", dest: "../../backend/static/assets" }
            ]
        })
    ],
    build: {
        outDir: "../backend/static",
        emptyOutDir: true,
        sourcemap: true
    },
    resolve: {
        preserveSymlinks: true,
        alias: {
            "@": path.resolve(__dirname, "./src")
        }
    },
    server: {
        proxy: {
            "/realtime": {
                target: "ws://localhost:8765",
                ws: true,
                rewriteWsOrigin: true
            }
        }
    }
});
