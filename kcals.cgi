#!/usr/bin/ruby

require 'cgi'
require 'tempfile'
require 'json'

cgi = CGI.new # https://ruby-doc.org/stdlib-1.9.3/libdoc/cgi/rdoc/CGI.html

def html_top
  return <<'HTML'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Kcals - estimate energy consumption when running or walking</title>
  </head>
  <body>
HTML
end

def html_bottom
  return <<'HTML'
  </body>
</html>
HTML
end

def about_method
  return <<'HTML'
    <p>
      The method used to calculate the energy expenditure is from
      <a href="http://jap.physiology.org/content/93/3/1039.full">Minetti et al.
      "Energy cost of walking and running at extreme uphill and downhill slopes,"
      J. Applied Physiology 93 (2002) 1039</a>,
      and is based on laboratory data from elite mountain runners on a treadmill.
      YMMV, and probably most of us are far less efficient than these guys.
      I find the data most useful if I want to compare
      one run to another, e.g., if I want to know how a mountain run with lots of elevation gain
      compares with a flat run at a longer distance.
    </p>
HTML
end

# Sample results:
# {"horiz":"14.42","horiz_unit":"mi","slope_distance":"14.42","gain":"0","vert_unit":"ft","cost":"1318","warnings":["The input file does not appear to contain any elevation data. Turn on the option 'dem' to try to download this."]} 
def format_output(r)
  if r.has_key?('warnings') then
    r['warnings'].each { |m|
      print "<p>warning: #{m}</p>\n"
    }
  end
  if r.has_key?('error') then
    print "<p>error: #{r['error']}</p>\n"
  end
  print <<"TABLE"
    <table>
      <tr>
        <td>horizontal distance</td>
        <td>#{r['horiz']} #{r['horiz_unit']}</td>
      </tr>
      <tr>
        <td>slope distance</td>
        <td>#{r['slope_distance']} #{r['horiz_unit']}</td>
      </tr>
      <tr>
        <td>gain</td>
        <td>#{r['gain']} #{r['vert_unit']}</td>
      </tr>
      <tr>
        <td>energy expended</td>
        <td>#{r['cost']} kcals</td>
      </tr>
    </table>
TABLE
  print about_method()
end

#---------------------------------------------------------

print cgi.header+"\n"+html_top

if !(cgi.has_key?('file')) then exit(-1) end

cgi_file = cgi['file'] # cgi_file is a StringIO object, which is a string that you can use file methods on

infile = Tempfile.new('kcals')
begin
  print "<h1>Kcals</h1>\n"
  #print "<p>#{Dir.pwd}</p>\n"
  infile << cgi_file.read # copy CGI upload data into temp file, which we will then read back
  #print `cat #{infile.path}`
  json = `CGI=1 ./kcals.rb verbosity=0 dem=1 <#{infile.path}` # verbosity=0 makes it output json data
  print "<!-- #{json} -->\n" # for debugging purposes
  results = JSON.parse(json)
  print format_output(results)
ensure
  # The following is supposed to happen automatically, but is good practice to do explicitly.
  print html_bottom
  infile.close
  infile.unlink
end