# frozen_string_literal: true

# Relabels the "necessary cookies only" button of the consent banner.
#
# al_cookie renders the banner from a template inside the gem with fixed
# English labels; its second button reads "Reject all". The button's behaviour
# is already "accept only the necessary category", so only the label changes.
# Registered in an after_init hook because gem plugins load after site plugins.

module SiteCookieConsentLabels
  FROM = 'acceptNecessaryBtn: "Reject all"'
  TO = 'acceptNecessaryBtn: "Accept only essentials"'

  def render_setup_script(context)
    script = super
    Jekyll.logger.warn 'cookie-consent-labels:', 'label not found; al_cookie template changed' unless script.include?(FROM)
    script.gsub(FROM, TO)
  end
end

Jekyll::Hooks.register :site, :after_init do |_site|
  if defined?(AlCookie) && !AlCookie.singleton_class.include?(SiteCookieConsentLabels)
    AlCookie.singleton_class.prepend(SiteCookieConsentLabels)
  end
end
