import subprocess
import re
import graphviz

URLS = [
    "google.com",
    "youtube.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "wikipedia.org",
    "amazon.com",
    "reddit.com",
    "netflix.com",
    "linkedin.com",
    "github.com",
    "stackoverflow.com",
    "apple.com",
    "microsoft.com",
    "nytimes.com",
    "cnn.com",
    "bbc.com",
    "espn.com",
    "twitch.tv",
    "discord.com",
    "cloudflare.com",
    "zoom.us",
]

HOP_RE = re.compile(
    r"^\s*(\d+)\s+"           
    r"(?:"
        r"(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)"  
        r"|(\d+\.\d+\.\d+\.\d+)"              
        r"|\*\s*\*\s*\*"                       
    r")"
)


def run_traceroute(url: str) -> list[str]:
    """
    Run `traceroute <url>` and return an ordered list of IP strings.
    Timed-out hops ('* * *') are skipped.
    """
    hops = []
    try:
        proc = subprocess.Popen(
            ["traceroute", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        while True:
            raw = proc.stdout.readline()
            if not raw:
                break
            line = raw.decode(errors="replace").strip()
            if not line:
                continue

            m = HOP_RE.match(line)
            if not m:
                continue  


            ip = m.group(3) or m.group(4)
            if ip:
                if not hops or hops[-1] != ip:
                    hops.append(ip)

        proc.wait()
    except FileNotFoundError:
        print("  [!] traceroute not found – is it installed?")
    except Exception as e:
        print(f"  [!] Error tracing {url}: {e}")

    return hops


def build_graph(urls: list[str]) -> graphviz.Graph:
    """Trace every URL and build a Graphviz undirected graph."""
    dot = graphviz.Graph("Internet", strict=True)
    dot.attr(rankdir="TB", overlap="false", splines="true")

    dot.node("origin", label="MY MACHINE", shape="star", style="filled", fillcolor="gold")

    for url in urls:
        print(f"Tracing {url} …")
        hops = run_traceroute(url)

        if not hops:
            print(f"  (no hops returned for {url})")
            continue

        dot.node(
            url,
            label=url,
            shape="rectangle",
            style="filled",
            fillcolor="lightblue",
        )

        path = ["origin"] + hops + [url]

        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]

            if src not in (url, "origin"):
                dot.node(src, shape="ellipse")
            if dst not in (url, "origin"):
                dot.node(dst, shape="ellipse")

            dot.edge(src, dst)

        print(f"  {len(hops)} hop(s) recorded.")

    return dot


def main():
    print("=" * 60)
    print("  Internet Path Mapper")
    print("=" * 60)

    dot = build_graph(URLS)

    output_path = "internet_map"
    dot.render(output_path, format="pdf", view=True, cleanup=True)
    print(f"\nGraph saved to '{output_path}.pdf'")


if __name__ == "__main__":
    main()