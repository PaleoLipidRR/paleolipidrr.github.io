# frozen_string_literal: true

# Site-local replacement for the `bust_css_cache` Liquid filter.
#
# The stock filter (jekyll-cache-bust, as patched by al_folio_core) digests the
# theme's own Sass only, so an edit to this site's _sass/ partials or to the
# local assets/css/main.scss override would leave the fingerprint on main.css
# unchanged and browsers would keep a stale stylesheet. This version digests
# the local _sass/ partials, the local main.scss and the installed
# al_folio_core version (so a theme upgrade also changes the fingerprint).
#
# Registered in an after_init hook so it takes precedence whatever the plugin
# load order is.

require 'digest'

module SiteCssCacheBust
  def bust_css_cache(file_name)
    source = @context.registers[:site].source
    files = Dir[File.join(source, '_sass', '**', '*')] + [File.join(source, 'assets', 'css', 'main.scss')]
    core = Gem.loaded_specs['al_folio_core']
    contents = files.select { |f| File.file?(f) }.sort.map { |f| File.read(f) }.join
    "#{file_name}?v=#{Digest::MD5.hexdigest("#{core&.version}#{contents}")}"
  end
end

Jekyll::Hooks.register :site, :after_init do |_site|
  Liquid::Template.register_filter(SiteCssCacheBust)
end
