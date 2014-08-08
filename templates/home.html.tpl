{% extends 'navigation.html.tpl' %}

{% block content %}
<div class="jumbotron">
    <div class="container">
        <!-- Main component for a primary marketing message or call to action -->
        <h1>Free IPv4/IPv6 to IPv6 Proxy</h1>
        <hr/>
        <p>
            <a href="http://v6proxy.com">
                <b>v6proxy</b>
            </a>
            provides access to your IPv6 capable HTTP and HTTPS servers via several domains hosted on the 
            <a href="http://cloudflare.com">
                <b>CloudFlare</b>
            </a>
            network.
        </p>
        <p>These domains allow registered users to point a subdomain to their publically accessable IPv6 host somewhere on the internet.</p>
        <p>
            Subdomains get the added benefits of the 
            <a href="http://cloudflare.com">
                <b>CloudFlare</b>
            </a>
            network including caching, added security, and SSL proxy support.
        </p>
        <p>
            <a class="btn btn-lg btn-primary" href="#" role="button"><i class="fa fa-book"></i> Read more</a>
            or
            <a class="btn btn-lg btn-success" href="#" role="button" data-toggle="modal" data-target="#registration-modal"><i class="fa fa-pencil-square-o"></i> Register a subdomain</a>
        </p>
        <hr/>
        <p>
        <h2>Similar Tools</h2>
        <ul class="list-unstyled">
            <li><a href="https://ngrok.com/">ngrok - Introspected tunnels to localhost</a></li>
        </ul>
        </p>
    </div>
</div>

{% end %}
