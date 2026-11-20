# frozen_string_literal: true

require 'bibtex'

# Exposes the citation-badge fields of the site's bibliography to the CV page as site.data.cv_pub_meta.
#
# The CV page (_data/cv.json) knows each publication by DOI; the Publications page gets its Google Scholar,
# Altmetric and Dimensions badges from fields of the BibTeX entries. This generator reads the same file that
# jekyll-scholar reads (the `scholar` settings of _config.yml) and builds a hash from the bare, lowercase DOI to
#   { "google_scholar_id" => String|nil, "altmetric" => String|nil, "dimensions" => String|nil }
# with each value as written in the bibliography ("true" means "use the DOI"), or nil when the field is absent.
# Entries without a DOI are skipped. A missing or unreadable file leaves an empty hash and logs a warning.
module SiteCvPubMeta
  FIELDS = %w[google_scholar_id altmetric dimensions].freeze
  DOI_PREFIX = %r{\Ahttps?://(?:dx\.)?doi\.org/}i.freeze

  # Lowercase DOI without a resolver prefix, or nil when absent or blank (an entry without a DOI is skipped quietly).
  def self.normalise_doi(value)
    text = plain(value)
    return nil if text.nil?

    doi = text.sub(DOI_PREFIX, '').strip.downcase
    doi.empty? ? nil : doi
  end

  # A field value as a plain string: outer braces and quotes stripped; nil when absent or empty.
  def self.plain(value)
    return nil if value.nil?

    text = value.to_s.strip
    text = text.sub(/\A[{"]+/, '').sub(/[}"]+\z/, '').strip
    text.empty? ? nil : text
  end

  def self.parse(path)
    meta = {}
    bibliography = BibTeX.open(path)
    bibliography.each do |entry|
      next unless entry.respond_to?(:key) && entry.respond_to?(:fields)

      begin
        doi = normalise_doi(entry[:doi])
        next if doi.nil?

        meta[doi] = FIELDS.to_h { |field| [field, plain(entry[field.to_sym])] }
      rescue StandardError => e
        Jekyll.logger.warn 'cv-pub-meta:', "skipped entry #{entry.key}: #{e.message}"
      end
    end
    meta
  end

  class Generator < Jekyll::Generator
    safe true

    def generate(site)
      site.data['cv_pub_meta'] = {}
      scholar = site.config['scholar'] || {}
      path = File.join(site.source, scholar['source'].to_s, scholar['bibliography'].to_s)
      unless File.file?(path)
        Jekyll.logger.warn 'cv-pub-meta:', "bibliography not found at #{path}; CV citation tags are off"
        return
      end

      site.data['cv_pub_meta'] = SiteCvPubMeta.parse(path)
    rescue StandardError => e
      Jekyll.logger.warn 'cv-pub-meta:', "could not read the bibliography (#{e.class}: #{e.message}); CV citation tags are off"
      site.data['cv_pub_meta'] ||= {}
    end
  end
end
