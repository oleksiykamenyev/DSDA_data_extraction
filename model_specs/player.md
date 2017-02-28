`string` **name**  
`string` **username** *unique*, matches `/\A[a-z\d_+-]+\z/`; if blank: 
```ruby
username = I18n.transliterate(name).downcase.strip.gsub(/\s+/, '_').gsub(/[^a-z\d_-]+/, '')
```
`string` **twitch** *optional*, matches `/\A[a-z\d_+-]+\z/`  
`string` **youtube** *optional*, matches `/\A[a-z\d_+-]+\z/`  
`has_many` **demos**  
