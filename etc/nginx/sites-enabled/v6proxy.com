upstream upstream_v6proxy_tornado {
    ip_hash;
    server  127.0.0.1:8081;
}

server {

    listen [::]80;

    server_name         v6proxy.com www.v6proxy.com;

    access_log          /var/log/nginx/v6proxy-access.log;
    error_log           /var/log/nginx/v6proxy-error.log;

    root                /home/spencersr/v6proxy/www/;

    gzip                on;
    gzip_proxied        any;
    gzip_types          text/plain text/css application/javascript application/xml application/json;
    
    # Proxy

    userid              on;
    userid_name         __uid;
    userid_path         /;
    userid_domain       .v6proxy.com;
    userid_expires      2d;
    userid_p3p          'policyref="/w3c/p3p.xml", CP="CUR ADM OUR NOR STA NID"';

    try_files           /system/maint.html $uri @v6proxy_tornado;

    location @v6proxy_tornado {

    	proxy_redirect      off;
        proxy_http_version  1.1;

        #BASIC PROXY STUFFS

        proxy_set_header    Host                        $host;
        proxy_set_header    X-Real-IP                   $remote_addr;
        
        proxy_set_header    X-Spdy                      $spdy;
        proxy_set_header    X-Spdy-Reqest-Priority      $spdy_request_priority;
        
        proxy_set_header    X-GeoIP-Country-Code        $geoip_country_code;
        proxy_set_header    X-GeoIP-Country-Code3       $geoip_country_code3;
        proxy_set_header    X-GeoIP-Country-Name        $geoip_country_name;
        proxy_set_header    X-GeoIP-City-Country-Code   $geoip_city_country_code;
        proxy_set_header    X-GeoIP-City-Country-Code3  $geoip_city_country_code3;
        proxy_set_header    X-GeoIP-City-Country-Name   $geoip_city_country_name;
        proxy_set_header    X-GeoIP-City-Continent-Code $geoip_city_continent_code;
        proxy_set_header    X-GeoIP-Region              $geoip_region;
        proxy_set_header    X-GeoIP-City                $geoip_city;
        proxy_set_header    X-GeoIP-Postal-Code         $geoip_postal_code;
        proxy_set_header    X-GeoIP-Latitude            $geoip_latitude;
        proxy_set_header    X-GeoIP-Longitude           $geoip_longitude;
        proxy_set_header    X-GeoIP-DMA-Code            $geoip_dma_code;
        proxy_set_header    X-GeoIP-Area-Code           $geoip_area_code;
                
        proxy_set_header    X-UserID-Set                $uid_set;
        proxy_set_header    X-UserID-Got                $uid_got;
        
        #END BASIC PROXY STUFFS        

        proxy_pass          http://upstream_v6proxy_tornado;

    }

}
