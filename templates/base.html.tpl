<!DOCTYPE html>
<html lang="en">
    
    <head>
        <meta charset="utf-8"/>
        <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
        <meta name="apple-mobile-web-app-capable" content="yes"/>
        <meta name="description" content=""/>
        <meta name="author" content=""/>
        
        <link rel="apple-touch-icon-precomposed" sizes="144x144" href="{{ static_url('ico/apple-touch-icon-144-precomposed.png') }}"/>
        <link rel="apple-touch-icon-precomposed" sizes="114x114" href="{{ static_url('ico/apple-touch-icon-114-precomposed.png') }}"/>
        <link rel="apple-touch-icon-precomposed" sizes="72x72" href="{{ static_url('ico/apple-touch-icon-72-precomposed.png') }}"/>
        <link rel="apple-touch-icon-precomposed" href="{{ static_url('ico/apple-touch-icon-57-precomposed.png') }}"/>
        
        <link rel="shortcut icon" href="{{ static_url('ico/favicon.png') }}"/>
        
        <title>{{ page_title_prefix }}::{{ page_title }}</title>
        
        <!-- Bootstrap core CSS -->
        <link href="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.2.0/css/bootstrap.min.css" rel="stylesheet"/>
        <link href="//cdnjs.cloudflare.com/ajax/libs/bootswatch/3.2.0+1/united/bootstrap.min.css" rel="stylesheet"/>
        
        <!-- FontAwesome Icons -->
        <link href="//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.1.0/css/font-awesome.min.css" rel="stylesheet"/>
        
        <!-- [if lt IE 9] >
          <script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="//cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js"></script>
        <![endif]-->
        
        <style>

            .navbar {
                margin-bottom: 0px;
            }

            .centered {
                text-align: center;
            }

        </style>
        
    </head>
    
    <body role="document">
        
        <a href="https://github.com/whardier/v6proxy"><img style="position: absolute; top: 0; left: 0; border: 0; z-index: 9999;" src="https://camo.githubusercontent.com/8b6b8ccc6da3aa5722903da7b58eb5ab1081adee/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f6c6566745f6f72616e67655f6666373630302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_left_orange_ff7600.png"></a>

        {% block registration_modal %}
        <!-- Modal -->
        <div class="modal fade" id="registration-modal" tabindex="-1" role="dialog" aria-labelledby="registration-modal-label" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                        <form class="form-horizontal" id='registration-modal-form' role="form" method="POST" action="{{ reverse_url('subdomain/registration') }}">
                            {% raw xsrf_form_html() %}

                            <div class="modal-header">
                                <button type="button" class="close" data-dismiss="modal">
                                    <span aria-hidden="true">&times;</span><span class="sr-only">Close</span>
                            </button>
                            <h4 class="modal-title" id="registration-modal-label">Subdomain Registration</h4>
                        </div>
                        <div class="modal-body">

                            <div class="row">
                                <div class="col-md-10 col-md-offset-1">
    
                                    <div class="form-group">
                                        <label for="email">Email address</label>
                                        <input type="email" class="form-control" name="email" id="email" placeholder="username@domain.com">
                                        <p class="help-block">Used for quick verification and abuse management.</p>
                                    </div>
                                    <div class="form-group">
                                        <label for="address">IPv6 Address</label>
                                        <input type="text" class="form-control" name="address" id="address" placeholder="address">
                                        <p class="help-block">Address should be publically accessible and be listening on standard HTTP and/or HTTPS ports.</p>
                                    </div>
                                    <div class="form-group">
                                        <label for="subdomain">Subdomain</label>
                                        <input type="text" class="form-control" name="subdomain" id="subdomain" placeholder="subdomain">
                                        <p class="help-block">You will be emailed further information about the subdomain you register which includes an unproxied DNS alias (direct).  You may use as many '.' as CloudFlare allows.</p>
                                    </div>
                                    <div class="form-group">
                                        <label for="domain">Domain</label>
                                        <select class="form-control" name="domain" id="domain">
                                            <option selected>v6proxy.com</option>
                                            <option>proxyipv6.com</option>
                                        </select>
                                    </div>
                                    <div class="checkbox">
                                        <label>
                                            <input type="checkbox" id="direct" name="direct" checked/> Direct AAAA record for <i>subdomain</i>.<b>direct</b>.<i>domain.com</i>
                                        </label>
                                    </div>
                                    <div class="checkbox">
                                        <label>
                                            <input type="checkbox" id="wildcard" name="wildcard" checked/> Direct AAAA <b>wildcard</b> record for <b>*</b>.<i>subdomain</i>.<b>wildcard</b>.<i>domain.com</i>
                                        </label>
                                    </div>
                                </div>
                            </div>

                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</a>
                            <button type="submit" id="registration-modal-form-button-accept" class="btn btn-default">Register</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        {% end %}

        {% block donation_modal %}
        <!-- Modal -->
        <div class="modal fade" id="donation-modal" tabindex="-1" role="dialog" aria-labelledby="donation-modal-label" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">
                            <span aria-hidden="true">&times;</span><span class="sr-only">Close</span>
                        </button>
                        <h4 class="modal-title" id="donation-modal-label">Consider donating</h4>
                    </div>
                    <div class="modal-body">
                        Donations are the only thing that really keep this service trucking along.
                    </div>
                    <div class="modal-footer">
                        <a href="#" id="donation-modal-button-reject" type="button" class="btn btn-default" data-dismiss="modal">Not today, thanks.</a>
                        <a href="{{ reverse_url('donation') }}" id="donation-modal-button-accept" type="button" class="btn btn-primary">I'm interested in donating.</a>
                    </div>
                </div>
            </div>
        </div>
        {% end %}

        <nav class="navbar navbar-default navbar-static-top" role="navigation">
            <div class="container">
                <!-- Brand and toggle get grouped for better mobile display -->
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="{{ reverse_url('home') }}">
                        <i class="fa fa-exchange"></i> <b>v6proxy</b>
                    </a>
                </div>
                
                <!-- Collect the nav links, forms, and other content for toggling -->
                <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                    <ul class="nav navbar-nav">
                        <li class="{% if page_title == 'Home' %}active{% end %}">
                            <a href="{{ reverse_url('home') }}"><i class="fa fa-home"></i> Home</a>
                        </li>
                        <li class="{% if page_title == 'Status' %}active{% end %}">
                            <a href="{{ reverse_url('status') }}"><i class="fa fa-tachometer"></i> Status</a>
                        </li>
                        <li class="{% if page_title == 'F.A.Q.' %}active{% end %}">
                            <a href="{{ reverse_url('faq') }}"><i class="fa fa-question-circle"></i> F.A.Q.</a>
                        </li>
                        <li class="{% if page_title == 'Donation' %}active{% end %}">
                            <a href="{{ reverse_url('donation') }}"><i class="fa fa-usd"></i> Donation</a>
                        </li>
                    </ul>
                    <ul class="nav navbar-nav navbar-right">
                        <li>
                            <a href="#" data-toggle="modal" data-target="#registration-modal">
                                <i class="fa fa-pencil-square-o"></i> Register a subdomain
                            </a>
                        </li>
                    </ul>
                </div>
                <!-- /.navbar-collapse -->
            </div>
            <!-- /.container -->
        </nav>
        
        {% block content %}
        {% end %}
        
        <footer>
            <div class="container">
                <div class="row centered">
                    <div class="col-lg-3">

                        <i class="fa fa-info" style="font-size: 10em"></i>
                        
                        <h4><b>About v6proxy</b></h4>
                        <p>
                            This is a free service made to promote 
                            <a href="http://en.wikipedia.org/wiki/IPv6">
                                <b>IPv6</b>
                            </a>
                            and promote 
                            <a href="http://cloudflare.com">
                                <b>CloudFlare</b>
                            </a>
                            as a simple IPv4/IPv6 to IPv6 proxy.
                        </p>
                    </div>
                    <div class="col-lg-3">

                        <i class="fa fa-cloud" style="font-size: 10em"></i>
                        
                        <h4><b>Domains</b></h4>
                        <p>*.v6proxy.com</p>
                        <p>*.proxyipv6.com</p>
                        <p>*.proxyv6.com</p>
                    </div>
                    <div class="col-lg-3">

                        <i class="fa fa-play" style="font-size: 10em"></i>

                        <h4><b>Getting Started</b></h4>
                        <p>
                            <a href="{{ reverse_url('ipv6') }}">Not on IPv6?</a>
                        </p>
                        <p>
                            <a href="{{ reverse_url('ssl') }}">SSL Setup</a>
                        </p>
                        <p>
                            <a href="#" data-toggle="modal" data-target="#registration-modal">
                                Register a subdomain
                            </a>
                        </p>
                    </div>
                    <div class="col-lg-3">

                        <i class="fa fa-share-alt" style="font-size: 10em"></i>

                        <h4>Sharing is caring</h4>
                        <p>You don't have to be the only cool kid on the block with this service working for them</p>

                        <iframe src="//ghbtns.com/github-btn.html?user=whardier&repo=v6proxy&type=watch&count=true&size=large" allowtransparency="true" frameborder="0" scrolling="0" width="170" height="30"></iframe>

                        <iframe src="//www.facebook.com/plugins/like.php?href=http%3A%2F%2Fv6proxy.com%2F&amp;width=170&amp;layout=button_count&amp;action=like&amp;show_faces=true&amp;share=true&amp;height=21&amp;appId=316795618495567" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:170px; height:21px;" allowTransparency="true"></iframe>

                        <a href="https://twitter.com/share" class="twitter-share-button" data-url="http://v6proxy.com/" data-text="Free IPv4/IPv6 to IPv6 Proxy - What's not to love?" data-via="whardier" data-size="large" data-related="whardier" data-hashtags="v6proxy">Tweet</a>
                        <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');</script>

                    </div>
                </div>
            </div>
        </div>
    </footer>
    
                <hr/>

    <div class="container">
        <div class="row">
            <div class="col-lg-12">
                <p>
                    <b>&copy; Brute Technologies 2014</b> and created by <a href="mailto:spencersr@brutetech.com">Shane R. Spencer (spencersr@brutetech.com)</a>
                </p>
            </div>
        </div>
    </div>
    
    <!-- Bootstrap core JavaScript ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery-cookie/1.4.1/jquery.cookie.min.js"></script>
    
    <script src="//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.2.0/js/bootstrap.min.js"></script>

    <script>
                        
        $(document).ready(function() {

            if (!$.cookie('donation')) {
                $('#donation-modal').modal('show')
            };
        
            $("#donation-modal-button-reject").click(function() {
                $.cookie('donation', 'r', { expires: 1, path: '/'});
            });

            $("#donation-modal-button-accept").click(function() {
                $.cookie('donation', 'a', { expires: 30, path: '/'});
            });

        });
               
    </script>
    
</body>

</html>
