FROM library/postgres

# Install required packages
RUN apt-get update && \
    apt-get -y install wget unzip ruby dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create data directory
RUN mkdir -p /data
WORKDIR /data/

# Download AdventureWorks directly from GitHub
RUN wget -q https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks-oltp-install-script.zip -O AdventureWorks-oltp-install-script.zip && \
    unzip -q AdventureWorks-oltp-install-script.zip && \
    rm AdventureWorks-oltp-install-script.zip

# Create inline Ruby script to process CSVs
RUN echo '#!/usr/bin/env ruby\n\
\n\
Dir.glob("./*.csv") do |csv_file|\n\
  f = if (is_needed = csv_file.end_with?("/Address.csv"))\n\
        File.open(csv_file, "rb:WINDOWS-1252:UTF-8")\n\
      else\n\
        File.open(csv_file, "rb:UTF-16LE:UTF-8")\n\
      end\n\
  output = ""\n\
  text = ""\n\
  is_first = true\n\
  is_pipes = false\n\
  begin\n\
  f.each do |line|\n\
    if is_first\n\
      if line.include?("+|")\n\
        is_pipes = true\n\
      end\n\
      if line[0] == "\uFEFF"\n\
        line = line[1..-1]\n\
        is_needed = true\n\
      end\n\
    end\n\
    is_first = false\n\
    break if !is_needed\n\
    if is_pipes\n\
      if line.strip.end_with?("&|")\n\
        text << line.gsub("|474946383961", "|\\\\\\\\x474946383961")\n\
                    .gsub(/"/, "\\"\\"")\n\
                    .strip[0..-3]\n\
        output << text.split("+|").map { |part|\n\
          (part[1] == "<" && part[-1] == ">") ? "\"" + part[1..-1] + "\"" :\n\
          (part.include?("\t") ? "\"" + part + "\"" : part)\n\
        }.join("\t")\n\
        output << "\n"\n\
        text = ""\n\
      else\n\
        text << line.gsub(/"/, "\\"\\"")\n\
                    .gsub("\r\n", "\\\\n")\n\
      end\n\
    else\n\
      output << line.gsub(/"/, "\\"\\"")\n\
                    .gsub(/\&\|\n/, "\n")\n\
                    .gsub(/\&\|\r\n/, "\n")\n\
                    .gsub("\tE6100000010C", "\t\\\\\\\\xE6100000010C")\n\
                    .gsub(/\r\n/, "\n")\n\
    end\n\
  end\n\
  if is_needed\n\
    puts "Processing #{csv_file}"\n\
    f.close\n\
    w = File.open(csv_file + ".xyz", "w")\n\
    w.write(output)\n\
    w.close\n\
    File.delete(csv_file)\n\
    File.rename(csv_file + ".xyz", csv_file)\n\
  end\n\
  rescue Encoding::InvalidByteSequenceError\n\
    f.close\n\
  end\n\
end\n' > /data/update_csvs.rb && \
    chmod +x /data/update_csvs.rb && \
    ruby /data/update_csvs.rb && \
    rm /data/update_csvs.rb

# Copy postgres-install.sql directly into the image
COPY postgres-install.sql /data/

# Create init script inline
RUN echo '#!/bin/bash\n\
\n\
export PGUSER=postgres\n\
psql <<- SHELL\n\
  CREATE USER docker;\n\
  CREATE DATABASE "Adventureworks";\n\
  GRANT ALL PRIVILEGES ON DATABASE "Adventureworks" TO docker;\n\
SHELL\n\
cd /data\n\
psql -d Adventureworks < /data/postgres-install.sql\n' > /docker-entrypoint-initdb.d/install.sh && \
    chmod +x /docker-entrypoint-initdb.d/install.sh && \
    dos2unix /docker-entrypoint-initdb.d/install.sh