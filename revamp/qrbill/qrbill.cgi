#!/usr/bin/perl

use strict;
use warnings;
use lib qw(lib /home/sts/perl5/lib/perl5/x86_64-linux-gnu-thread-multi);

use CGI;
#use CGI::Carp 'fatalsToBrowser';
use SL::Helper::QrBill;

my @html = split /\n###\n/, do { local $/; <DATA> };

my $query = CGI->new;

my $action = $query->param('action');

if ($action eq 'generate') {
  my %h;
  foreach my $param ($query->param) {
     $h{$param} = $query->param($param);
  }
  my @hrefs = (
    { iban => $h{biller_iban} },
    { address_type => $h{biller_address_type},
      company => $h{biller_company},
      address_row1 => $h{biller_address_row1},
      address_row2 => $h{biller_address_row2},
      street => $h{biller_street},
      street_no => $h{biller_street_no},
      postalcode => $h{biller_postalcode},
      city => $h{biller_city},
      countrycode => $h{biller_countrycode} },
    { amount => $h{payment_amount},
      currency => $h{payment_currency} },
    { address_type => $h{recipient_address_type},
      name => $h{recipient_name},
      address_row1 => $h{recipient_address_row1},
      address_row2 => $h{recipient_address_row2},
      street => $h{recipient_street},
      street_no => $h{recipient_street_no},
      postalcode => $h{recipient_postalcode},
      city => $h{recipient_city},
      countrycode => $h{recipient_countrycode} },
    { type => $h{ref_nr_type},
      ref_number => $h{ref_nr_number} },
    { unstructured_message => $h{additional_unstructured_message} },
  );
  eval { SL::Helper::QrBill->new(@hrefs)->generate(); };
  if ($@) {
    form($@);
  }
  else {
    print <<"HTML";
Content-Type: text/html

$html[1]
HTML
  }
}
else {
  form();
}

sub form
{
  my ($error) = @_;
  chomp $error;
  my $html = $html[0];
  $html =~ s/\$ERROR/$error/;
  $html =~ s/\$VERSION/$SL::Helper::QrBill::VERSION/;
  print <<"HTML";
Content-Type: text/html

$html
HTML
}

__DATA__
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <link rel="stylesheet" type="text/css" href="qrbill.css">
    <title>QrBill.pm Generator</title>
  </head>
  <body>
    <form method="post" accept-charset="utf-8" action="./">
      <input type="hidden" name="action" value="generate">
      <h3><a href="https://github.com/kivitendo/kivitendo-erp/blob/master/SL/Helper/QrBill.pm" target="_blank">QrBill.pm</a> Generator <code>(v$VERSION)</code></h3>
      <table>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>biller information</b></td>
        </tr>
        <tr>
          <td class="td">IBAN:</td><td><input type="text" name="biller_iban" value=""></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>biller data</b></td>
        </tr>
        <tr>
          <td class="td">Address Type:</td><td>K <input type="radio" name="biller_address_type" value="K"> S <input type="radio" name="biller_address_type" value="S"></td>
        </tr>
        <tr>
          <td class="td">Company:</td><td><input type="text" name="biller_company" value=""></td>
        </tr>
        <tr>
          <td class="td">Address Row1:</td><td><input type="text" name="biller_address_row1" value=""></td>
        </tr>
        <tr>
          <td class="td">Address Row2:</td><td><input type="text" name="biller_address_row2" value=""></td>
        </tr>
        <tr>
          <td class="td">Street:</td><td><input type="text" name="biller_street" value=""></td>
        </tr>
        <tr>
          <td class="td">Street No:</td><td><input type="text" name="biller_street_no" value=""></td>
        </tr>
        <tr>
          <td class="td">Postalcode:</td><td><input type="text" name="biller_postalcode" value=""></td>
        </tr>
        <tr>
          <td class="td">City:</td><td><input type="text" name="biller_city" value=""></td>
        </tr>
        <tr>
          <td class="td">Countrycode:</td><td><input type="text" name="biller_countrycode" value=""></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>payment information</b></td>
        </tr>
        <tr>
          <td class="td">Amount:</td><td><input type="text" name="payment_amount" value=""></td>
        </tr>
        <tr>
          <td class="td">Currency:</td><td><select name="payment_currency"><option selected>CHF</option><option>EUR</option></select></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>invoice recipient data</b></td>
        </tr>
        <tr>
          <td class="td">Address Type:</td><td>K <input type="radio" name="recipient_address_type" value="K"> S <input type="radio" name="recipient_address_type" value="S"></td>
        </tr>
        <tr>
          <td class="td">Name:</td><td><input type="text" name="recipient_name" value=""></td>
        </tr>
        <tr>
          <td class="td">Address Row1:</td><td><input type="text" name="recipient_address_row1" value=""></td>
        </tr>
        <tr>
          <td class="td">Address Row2:</td><td><input type="text" name="recipient_address_row2" value=""></td>
        </tr>
        <tr>
          <td class="td">Street:</td><td><input type="text" name="recipient_street" value=""></td>
        </tr>
        <tr>
          <td class="td">Street No:</td><td><input type="text" name="recipient_street_no" value=""></td>
        </tr>
        <tr>
          <td class="td">Postalcode:</td><td><input type="text" name="recipient_postalcode" value=""></td>
        </tr>
        <tr>
          <td class="td">City:</td><td><input type="text" name="recipient_city" value=""></td>
        </tr>
        <tr>
          <td class="td">Countrycode:</td><td><input type="text" name="recipient_countrycode" value=""></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>reference number data</b></td>
        </tr>
        <tr>
          <td class="td">Type:</td><td><select name="ref_nr_type"><option selected>QRR</option><option>NON</option></select></td>
        </tr>
        <tr>
          <td class="td">Ref Number:</td><td><input type="text" name="ref_nr_number" value=""></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
        <tr>
          <td colspan="2"><b>additional information</b></td>
        </tr>
        <tr>
          <td class="td">Unstructured Message:</td><td><input type="text" name="additional_unstructured_message" value=""></td>
        </tr>
        <tr>
          <td colspan="2"><hr></td>
        </tr>
      </table>
      <font color="red">$ERROR</font><br>
      <input type="submit" value="generate"> <input type="reset" value="reset"><br>
    </form>
  </body>
</html>
###
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
       "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <link rel="stylesheet" type="text/css" href="qrbill.css">
    <title>QrBill.pm Generator</title>
  </head>
  <body>
    <img src="out.png"><br><br>
    <a href="javascript:history.back()">return</a>
  </body>
</html>
