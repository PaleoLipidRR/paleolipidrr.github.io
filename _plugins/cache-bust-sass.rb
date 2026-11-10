# frozen_string_literal: true

# Site-local replacement for the `bust_css_cache` Liquid filter.
#
# The jekyll-cache-bust gem digests the directory 'assets/_sass', which does
# not exist, so the fingerprint on main.css never changes and browsers keep a
# stale stylesheet after a style edit. This version digests what main.css is
# actually compiled from: the local _sass/ partials, the local
# assets/css/main.scss, and the installed al_folio_core version (so a theme
# upgrade also changes the fingerprint).
#
# Site plugins load before gem plugins, so the filter is registered in an
# after_init hook to make it take precedence over the gem's.

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
