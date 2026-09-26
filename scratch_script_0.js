
    let globalProvinces = [];
    let leafletMapInstance = null;
    let leafletMarkersMap = {};

    const provinceCoordinates = {
      "koshi": [26.8124, 87.2834],
      "madhesh": [26.9124, 85.9234],
      "bagmati": [27.7172, 85.3240],
      "gandaki": [28.2096, 83.9856],
      "lumbini": [27.6866, 83.4323],
      "karnali": [28.6019, 81.6339],
      "sudurpashchim": [28.6944, 80.5906]
    };

    document.addEventListener('DOMContentLoaded', () => {
      // Critical above-the-fold data first; defer heavier sections.
      loadNewsFlashes();
      loadStats();
      loadSettings();
      loadProvinces();
      checkPopup();
      initSmoothExperience();

      const deferHeavy = () => {
        loadGallery();
        loadVideos();
        loadNews();
        loadResources();
        loadTeam();
        loadCollaborations();
      };
      if ('requestIdleCallback' in window) {
        requestIdleCallback(deferHeavy, { timeout: 1200 });
      } else {
        setTimeout(deferHeavy, 200);
      }

      window.addEventListener('scroll', () => {
        const btn = document.getElementById('backToTop');
        if (window.scrollY > 350) {
          btn.classList.add('visible');
        } else {
          btn.classList.remove('visible');
        }
      }, { passive: true });
    });

    function initSmoothExperience() {
      const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      document.querySelectorAll('.hero, .about-overview-section, .provinces-section, .map-section, .news-resources, .cta-banner, .footer')
        .forEach((el, idx) => {
          if (idx > 0) el.classList.add('content-soft');
          if (!prefersReduced) {
            el.classList.add('reveal');
            if (idx === 0) el.classList.add('is-visible');
          }
        });

      if (!prefersReduced && 'IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-visible');
              io.unobserve(entry.target);
            }
          });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
        document.querySelectorAll('.reveal').forEach((el) => io.observe(el));
      } else {
        document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-visible'));
      }

      document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener('click', (e) => {
          const id = link.getAttribute('href');
          if (!id || id === '#') return;
          const target = document.querySelector(id);
          if (!target) return;
          e.preventDefault();
          const navLinks = document.getElementById('navLinks');
          if (navLinks) navLinks.classList.remove('active');
          target.scrollIntoView({ behavior: prefersReduced ? 'auto' : 'smooth', block: 'start' });
        });
      });
    }

    function animateLoaded(container) {
      if (!container) return;
      container.classList.remove('fade-in-children');
      void container.offsetWidth;
      container.classList.add('fade-in-children');
    }

    function toggleMobileMenu() {
      const navLinks = document.getElementById('navLinks');
      navLinks.classList.toggle('active');
    }

    function scrollToTop() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function setElementText(id, value) {
      const el = document.getElementById(id);
      if (el) el.innerText = value;
    }


    async function loadSettings() {
      try {
        const res = await fetch('/api/settings/');
        if (res.ok) {
          const data = await res.json();
          // Hero image is now rendered server-side to prevent flash of unstyled content
        }
      } catch(e) {}
    }
\n    async function loadStats() {
      try {
        const res = await fetch('/api/stats/');
        if (res.ok) {
          const data = await res.json();
          setElementText('statProvinces', data.provincial_networks || '7');
          setElementText('statDefenders', data.monitored_defenders || '1,200+');
          setElementText('statCases', data.resolved_cases || '150+');
          const visVal = (data.total_visitors || 0).toLocaleString();
          setElementText('totalVisitors', visVal);
          setElementText('footerTotalVisitors', visVal);
        }
      } catch (e) {
        console.error("Failed to load stats:", e);
      }
    }

    function getProvinceDistricts(name) {
      if (!name) return 10;
      const n = name.toLowerCase();
      if (n.includes('koshi')) return 14;
      if (n.includes('madhesh')) return 8;
      if (n.includes('bagmati')) return 13;
      if (n.includes('gandaki')) return 11;
      if (n.includes('lumbini')) return 12;
      if (n.includes('karnali')) return 10;
      if (n.includes('sudurpashchim')) return 9;
      return 10;
    }

    async function loadProvinces() {
      try {
        const res = await fetch('/api/provinces/');
        if (res.ok) {
          globalProvinces = await res.json();
          const grid = document.getElementById('provinceGrid');
          if (!grid) return;

          if (!globalProvinces || globalProvinces.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px; background: #f8fafc; border: 1px dashed var(--border-color); border-radius: 8px;">No provincial helpdesks registered yet.</div>`;
            return;
          }

          grid.innerHTML = globalProvinces.map((p, idx) => {
            const distCount = p.districts_count || getProvinceDistricts(p.name);
            return `
              <div class="province-card" onclick="openProvinceDetail(${p.id})">
                <div>
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <h4 style="margin: 0; font-size: 16px; font-weight: 800; color: var(--primary-navy);">${p.name}</h4>
                    <span style="font-size: 10px; font-weight: 800; background: #e0f2fe; color: #0284c7; padding: 3px 10px; border-radius: 12px; border: 1px solid #bae6fd;">PROVINCE ${idx + 1}</span>
                  </div>
                  <p style="font-weight: 700; color: #1e293b; margin-bottom: 8px; font-size: 13px;">
                    <i class="fa-solid fa-location-dot" style="color: #0288D1; margin-right: 5px;"></i>${p.base_city} &bull; <span style="color: #059669;">${distCount} Districts</span>
                  </p>
                  <p style="font-size: 13px; color: #475569; line-height: 1.55; margin-bottom: 12px;">${p.description || ''}</p>
                </div>
                <div class="btn-view-province">Inspect Desk Detail & Contact <i class="fa-solid fa-arrow-right"></i></div>
              </div>
            `;
          }).join('');

          animateLoaded(grid);
          initLeafletMap(globalProvinces);
        }
      } catch (e) {
        console.error("Failed to load provinces:", e);
      }
    }

    function whenLeafletReady(callback, attempts = 40) {
      if (typeof L !== 'undefined') {
        callback();
        return;
      }
      if (attempts <= 0) {
        console.warn('Leaflet failed to load');
        return;
      }
      setTimeout(() => whenLeafletReady(callback, attempts - 1), 50);
    }

    function initLeafletMap(provinces) {
      whenLeafletReady(() => {
        if (!document.getElementById('leafletMap')) return;
        if (leafletMapInstance) leafletMapInstance.remove();

        const thapagaunCoords = [27.6939, 85.3340];

        leafletMapInstance = L.map('leafletMap', {
          center: thapagaunCoords,
          zoom: 15,
          scrollWheelZoom: false
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; OpenStreetMap contributors'
        }).addTo(leafletMapInstance);

        const marker = L.marker(thapagaunCoords).addTo(leafletMapInstance);
        marker.bindPopup(`
          <div style="font-size: 13px; padding: 6px; min-width: 200px;">
            <strong style="color: #092347; font-size: 14px;">Human Rights Defenders Forum Nepal</strong><br>
            <span style="color: #475569;">Thapagaun, New Baneshwor, Kathmandu, Nepal</span><br>
            <a href="tel:+9779851180690" style="display: inline-block; margin-top: 6px; background: #0D47A1; color: #ffffff; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 11px; text-decoration: none;"><i class="fa-solid fa-phone"></i> +977 985-1180690</a>
          </div>
        `).openPopup();

        setTimeout(() => {
          leafletMapInstance.invalidateSize();
        }, 400);
      });
    }

    function openProvinceDetail(id) {
      const p = globalProvinces.find(item => item.id === id);
      if (!p) return;

      const distCount = p.districts_count || getProvinceDistricts(p.name);
      document.getElementById('provModalTitle').innerHTML = `<i class="fa-solid fa-shield-halved" style="color: var(--cobalt-accent);"></i> ${p.name}`;
      document.getElementById('provModalBody').innerHTML = `
        <div style="background: #f8fafc; border: 1px solid var(--border-color); padding: 18px; border-radius: 12px; margin-bottom: 18px;">
          <h4 style="color: var(--primary-navy); font-size: 16px; margin-bottom: 6px; font-weight: 800;">${p.base_city} Helpdesk Office</h4>
          <p style="color: var(--text-muted); font-size: 12.5px; margin-bottom: 12px;"><i class="fa-solid fa-location-dot" style="color: var(--cobalt-accent);"></i> ${p.address || 'Provincial Center Complex'}</p>
          <div style="display: flex; gap: 10px; flex-wrap: wrap;">
            <a href="tel:${p.helpline_phone}" style="background: #be123c; color: #fff; padding: 7px 14px; border-radius: 6px; font-weight: 700; font-size: 12px; text-decoration: none;"><i class="fa-solid fa-phone"></i> Helpline: ${p.helpline_phone}</a>
            <span style="background: #e0f2fe; color: #0284c7; padding: 7px 14px; border-radius: 6px; font-weight: 700; font-size: 12px;">${distCount} Districts</span>
            <span style="background: #fef3c7; color: #b45309; padding: 7px 14px; border-radius: 6px; font-weight: 700; font-size: 12px;">${p.active_cases || 0} Active Cases</span>
          </div>
        </div>
        <p style="line-height: 1.65; color: var(--text-body); margin-bottom: 20px;">${p.long_summary || p.description || ''}</p>
        <button onclick="closeProvinceModal(); openIncidentModal();" class="btn-submit" style="background: linear-gradient(135deg, #be123c 0%, #9f1239 100%);"><i class="fa-solid fa-triangle-exclamation"></i> Report Incident Alert to ${p.base_city} Desk</button>
      `;
      document.getElementById('provinceModal').classList.add('active');

      if (leafletMarkersMap[id] && leafletMapInstance) {
        leafletMapInstance.panTo(leafletMarkersMap[id].getLatLng());
        leafletMarkersMap[id].openPopup();
      }
    }

    async function loadNews() {
      try {
        const res = await fetch('/api/news/');
        if (res.ok) {
          const allNews = await res.json();
          const happenings = [];
          const orgUpdates = [];

          allNews.forEach(item => {
            const cat = (item.category || '').toLowerCase();
            if (cat.includes('update') || cat.includes('announcement') || cat.includes('notice') || cat.includes('org')) {
              orgUpdates.push(item);
            } else {
              happenings.push(item);
            }
          });

          renderNewsItems('newsListHappenings', happenings, 'No recent news recorded yet.');
          renderNewsItems('newsListOrgUpdates', orgUpdates, 'No organizational updates recorded yet.');
        }
      } catch (e) {}
    }

    function renderNewsItems(containerId, items, emptyMsg) {
      const container = document.getElementById(containerId);
      if (!container) return;
      if (!items || items.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-muted); font-size: 12px; padding: 20px;">${emptyMsg}</div>`;
        return;
      }
      container.innerHTML = items.map(item => `
        <a href="/news/${item.id}/" class="news-item" style="text-decoration: none; color: inherit; display: flex; gap: 16px;">
          ${item.image_url ? `<img src="${item.image_url}" alt="${item.title}" class="news-thumb">` : ''}
          <div style="flex: 1;">
            <div style="display: flex; gap: 6px; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 10px; background: #f1f5f9; color: var(--primary-navy); padding: 2px 7px; border-radius: 4px; font-weight: 700;">${item.published_date || 'Recent'}</span>
              <span style="font-size: 10px; background: #e0f2fe; color: #0284c7; padding: 2px 7px; border-radius: 4px; font-weight: 600;">${item.category || 'Rights'}</span>
            </div>
            <h5 style="font-size: 13.5px; font-weight: 700; color: var(--primary-navy); line-height: 1.35; margin: 0 0 4px 0;">${item.title}</h5>
            <p style="font-size: 11.5px; color: var(--text-muted); margin: 0;">${item.summary || ''}</p>
          </div>
        </a>
      `).join('');
      animateLoaded(container);
    }

    async function openNewsArticleModal(id) {
      try {
        const res = await fetch(`/api/news/${id}/`);
        if (res.ok) {
          const n = await res.json();
          
          document.getElementById('newsModalTitle').innerText = n.title;
          document.getElementById('newsModalDate').innerText = n.published_date || 'Recent Bulletin';
          
          if (n.image_url) {
            document.getElementById('newsModalImgContainer').style.display = 'block';
            document.getElementById('newsModalImg').src = n.image_url;
          } else {
            document.getElementById('newsModalImgContainer').style.display = 'none';
          }
          
          let contentText = n.content || n.summary || '';
          let htmlContent = contentText;
          if (!htmlContent.includes('<p>') && !htmlContent.includes('<br>')) {
              htmlContent = htmlContent.replace(/\n/g, '<br><br>');
          }
          document.getElementById('newsModalContent').innerHTML = htmlContent;
          
          document.getElementById('newsArticleModal').classList.add('active');
        }
      } catch (e) {}
    }

    async function loadResources() {
      try {
        const res = await fetch('/api/resources/');
        if (res.ok) {
          const resources = await res.json();
          const reports = resources.filter(r => (r.category || '').toLowerCase().includes('report'));
          const pubs = resources.filter(r => (r.category || '').toLowerCase().includes('pub'));
          const bylaws = resources.filter(r => (r.category || '').toLowerCase().includes('by-law') || (r.category || '').toLowerCase().includes('bylaw'));

          renderResourceList('gridReport', reports, 'Report');
          renderResourceList('gridPublication', pubs, 'Publication');
          renderResourceList('gridBylaws', bylaws, 'By-Laws');
        }
      } catch (e) {}
    }

    function renderResourceList(elementId, items, categoryType) {
      const container = document.getElementById(elementId);
      if (!container) return;
      if (items.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 12px; padding: 12px;">No ${categoryType} documents listed.</div>`;
        return;
      }
      container.innerHTML = items.map(r => `
        <div style="background: #ffffff; border: 1px solid var(--border-color); padding: 14px 18px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between; gap: 16px;">
          <div>
            <h5 style="margin: 0 0 3px 0; font-size: 14px; font-weight: 700; color: var(--primary-navy);">${r.title}</h5>
            <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">${r.format || 'PDF'} &bull; ${r.file_size || 'Document'}</span>
          </div>
          <button data-id="${r.id}" data-title="${r.title.replace(/"/g, '&quot;')}" onclick="openGatedDownload(this.getAttribute('data-id'), this.getAttribute('data-title'))" class="btn-hero-primary" style="padding: 7px 16px; font-size: 12px;"><i class="fa-solid fa-download"></i> Download</button>
        </div>
      `).join('');
    }

    function openGatedDownload(resId, title) {
      document.getElementById('gatedResourceId').value = resId;
      document.getElementById('gatedResourceTitle').value = title;
      document.getElementById('gatedModal').classList.add('active');
    }

    async function handleGatedSubmit(e) {
      e.preventDefault();
      
      const newTab = window.open('about:blank', '_blank');
      if (newTab) newTab.document.write("<div style='font-family: sans-serif; padding: 20px;'>Authorizing download...</div>");

      const payload = {
        resource_id: document.getElementById('gatedResourceId').value,
        user_name: document.getElementById('gatedUserName').value,
        user_email: document.getElementById('gatedUserEmail').value
      };

      try {
        const res = await fetch('/api/resource/download-access/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content') },
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
          showToast(data.message, 'success');
          closeGatedModal();
          document.getElementById('gatedForm').reset();
          if (data.download_url) {
            const finalUrl = new URL(data.download_url, window.location.origin).href;
            if (newTab) newTab.location.href = finalUrl;
            else window.open(finalUrl, '_blank');
          } else {
            if (newTab) newTab.close();
          }
        } else {
          if (newTab) newTab.close();
          showToast(data.error || 'Failed to authorize download', 'error');
        }
      } catch (err) {
        if (newTab) newTab.close();
        showToast('Error requesting access', 'error');
      }
    }

    async function handleMembershipSubmit(e) {
      e.preventDefault();
      const payload = {
        full_name: document.getElementById('mFullName').value,
        email: document.getElementById('mEmail').value,
        phone: document.getElementById('mPhone').value,
        province: document.getElementById('mProvince').value,
        organization: document.getElementById('mOrg').value,
        role: document.getElementById('mRole').value
      };

      try {
        const res = await fetch('/api/membership/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content') },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(data.message, 'success');
          document.getElementById('membershipForm').reset();
          closeMembershipModal();
        } else {
          showToast(data.error || 'Submission failed', 'error');
        }
      } catch (err) {
        showToast('Network error on submission', 'error');
      }
    }

    async function handleIncidentSubmit(e) {
      e.preventDefault();
      const payload = {
        reporter_name: document.getElementById('iName').value,
        contact_info: document.getElementById('iContact').value,
        province: document.getElementById('iProvince').value,
        incident_type: document.getElementById('iType').value,
        details: document.getElementById('iDetails').value
      };

      try {
        const res = await fetch('/api/incident/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content') },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(data.message, 'success');
          document.getElementById('incidentForm').reset();
          closeIncidentModal();
        } else {
          showToast(data.error || 'Failed to log report', 'error');
        }
      } catch (err) {
        showToast('Network error on incident submission', 'error');
      }
    }

    async function loadTeam() {
      try {
        const res = await fetch('/api/team/');
        if (res.ok) {
          const team = await res.json();
          const grid = document.getElementById('teamGridDisplay');
          if (!grid) return;
          grid.innerHTML = team.map(member => `
            <div class="team-card">
              <img src="${member.image_url || 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&q=80'}" alt="${member.name}" class="team-avatar">
              <h4>${member.name}</h4>
              <span style="font-size: 11px; font-weight: 700; color: #0284c7; background: #e0f2fe; padding: 3px 10px; border-radius: 12px; display: inline-block; margin-bottom: 10px;">${member.designation}</span>
              <p>${member.bio || ''}</p>
            </div>
          `).join('');
          animateLoaded(grid);
        }
      } catch (e) {}
    }

    async function loadCollaborations() {
      try {
        const res = await fetch('/api/collaborations/');
        if (res.ok) {
          const collabs = await res.json();
          const grid = document.getElementById('collabGridDisplay');
          if (!grid) return;
          grid.innerHTML = collabs.map(c => `
            <div class="collab-card">
              <img src="${c.logo_url || 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=300&q=80'}" alt="${c.name}" class="collab-logo">
              <div>
                <h5 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 800; color: var(--primary-navy);">${c.name}</h5>
                <span style="font-size: 10px; font-weight: 700; color: #0d9488; background: #ccfbf1; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 6px;">${c.category || 'Institutional'}</span>
                <p style="margin: 0; font-size: 12px; color: var(--text-muted);">${c.blurb || ''}</p>
              </div>
            </div>
          `).join('');
          animateLoaded(grid);
        }
      } catch (e) {}
    }

    let globalGalleryPhotos = [];
    let currentGalleryIndex = 0;

    async function loadGallery() {
      try {
        const res = await fetch('/api/gallery/');
        if (res.ok) {
          globalGalleryPhotos = await res.json();
          const grid = document.getElementById('galleryGrid');
          if (!grid) return;
          if (globalGalleryPhotos.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No gallery photos available yet.</div>`;
            return;
          }
          grid.innerHTML = globalGalleryPhotos.map((g, idx) => `
            <div class="gallery-card" onclick="openGalleryLightbox(${idx})">
              <img src="${g.image_url}" alt="${g.title}" class="gallery-img">
              <div class="gallery-info">
                <span class="gallery-tag">${g.category || 'Advocacy'}</span>
                <h5>${g.title}</h5>
              </div>
            </div>
          `).join('');
          animateLoaded(grid);
        }
      } catch (e) {}
    }

    function openGalleryLightbox(index) {
      if (!globalGalleryPhotos || !globalGalleryPhotos[index]) return;
      currentGalleryIndex = index;
      const photo = globalGalleryPhotos[index];
      document.getElementById('lightboxImg').src = photo.image_url || '';
      document.getElementById('lightboxTitle').innerText = photo.title || '';
      document.getElementById('galleryLightboxModal').classList.add('active');
    }

    function closeGalleryLightbox() { document.getElementById('galleryLightboxModal').classList.remove('active'); }
    function prevGalleryPhoto() { if (currentGalleryIndex > 0) openGalleryLightbox(currentGalleryIndex - 1); }
    function nextGalleryPhoto() { if (currentGalleryIndex < globalGalleryPhotos.length - 1) openGalleryLightbox(currentGalleryIndex + 1); }

    let globalVideos = [];
    async function loadVideos() {
      try {
        const res = await fetch('/api/videos/');
        if (res.ok) {
          globalVideos = await res.json();
          const grid = document.getElementById('videoGrid');
          if (!grid) return;
          grid.innerHTML = globalVideos.map((v, idx) => `
            <div class="video-card" onclick="openVideoPlayerModal(${idx})" style="background: #ffffff; border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; cursor: pointer; transition: all 0.2s ease;">
              <div style="background: #f1f5f9; height: 120px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                <i class="fa-solid fa-circle-play" style="font-size: 36px; color: var(--cobalt-accent);"></i>
              </div>
              <h5 style="font-size: 14px; font-weight: 700; color: var(--primary-navy); margin-bottom: 4px;">${v.title}</h5>
              <span style="font-size: 11px; color: var(--text-muted); font-weight: 600;">${v.category || 'Documentary'}</span>
            </div>
          `).join('');
          animateLoaded(grid);
        }
      } catch (e) {}
    }

    function openVideoPlayerModal(idx) {
      if (!globalVideos[idx]) return;
      const v = globalVideos[idx];
      document.getElementById('videoModalTitle').innerText = v.title;
      document.getElementById('videoIframe').src = v.embed_url || '';
      document.getElementById('videoPlayerModal').classList.add('active');
    }

    function closeVideoPlayerModal() {
      document.getElementById('videoIframe').src = '';
      document.getElementById('videoPlayerModal').classList.remove('active');
    }

    async function loadNewsFlashes() {
      try {
        const res = await fetch('/api/news-flashes/');
        if (res.ok) {
          const flashes = await res.json();
          const bar = document.getElementById('newsTickerBar');
          const track = document.getElementById('tickerTrack');
          if (!flashes || flashes.length === 0) {
            bar.style.display = 'none';
            return;
          }
          const html = flashes.map(f => `<span><i class="fa-solid fa-angle-right"></i> ${f.text}</span>`).join('');
          track.innerHTML = html + html;
          bar.style.display = 'block';
        }
      } catch (e) {}
    }

    async function checkPopup() {
      if (sessionStorage.getItem('popupDismissed') === '1') return;
      try {
        const res = await fetch('/api/popup/');
        if (res.ok) {
          const popup = await res.json();
          if (popup.active === 1 && popup.title) {
            document.getElementById('popupTitle').innerText = popup.title;
            document.getElementById('popupSubtitle').innerText = popup.subtitle || '';
            const link = document.getElementById('popupLink');
            if (popup.link_url) link.href = popup.link_url;
            if (popup.link_text) link.innerText = popup.link_text;
            document.getElementById('popupModal').classList.add('active');
          }
        }
      } catch (e) {}
    }

    function closePopupModal() {
      sessionStorage.setItem('popupDismissed', '1');
      document.getElementById('popupModal').classList.remove('active');
    }

    function showToast(message, type = 'success') {
      const container = document.getElementById('toastContainer');
      const toast = document.createElement('div');
      // map django message tags if needed (e.g. error)
      const mappedType = type === 'error' ? 'error' : 'success';
      toast.className = `toast ${mappedType}`;
      toast.innerHTML = `<i class="fa-solid ${mappedType === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i><span>${message}</span>`;
      container.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }

    function openMembershipModal() { document.getElementById('membershipModal').classList.add('active'); }
    function closeMembershipModal() { document.getElementById('membershipModal').classList.remove('active'); }
    function openIncidentModal() { document.getElementById('incidentModal').classList.add('active'); }
    function closeIncidentModal() { document.getElementById('incidentModal').classList.remove('active'); }
    function closeProvinceModal() { document.getElementById('provinceModal').classList.remove('active'); }
    function closeGatedModal() { document.getElementById('gatedModal').classList.remove('active'); }
    function closeNewsArticleModal() { document.getElementById('newsArticleModal').classList.remove('active'); }
    function openAboutModal() { document.getElementById('aboutModal').classList.add('active'); }
    function closeAboutModal() { document.getElementById('aboutModal').classList.remove('active'); }
    function openResourcesModal() { document.getElementById('resourcesModal').classList.add('active'); }
    function closeResourcesModal() { document.getElementById('resourcesModal').classList.remove('active'); }
    function openMediaGalleryModal(tab) {
      if (tab) switchMediaTab(tab);
      document.getElementById('mediaGalleryModal').classList.add('active');
    }
    function closeMediaGalleryModal() { document.getElementById('mediaGalleryModal').classList.remove('active'); }

    function switchMediaTab(tab) {
      const photosTab = document.getElementById('mediaPhotosTab');
      const videosTab = document.getElementById('mediaVideosTab');
      const btnPhotos = document.getElementById('mediaTabBtnPhotos');
      const btnVideos = document.getElementById('mediaTabBtnVideos');

      if (tab === 'photos') {
        photosTab.style.display = 'block';
        videosTab.style.display = 'none';
        btnPhotos.classList.add('active');
        btnVideos.classList.remove('active');
      } else {
        photosTab.style.display = 'none';
        videosTab.style.display = 'block';
        btnVideos.classList.add('active');
        btnPhotos.classList.remove('active');
      }
    }

    function filterAboutSequence(sec, btn) {
      document.querySelectorAll('#aboutModal .sub-pill-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const s1 = document.getElementById('seqAboutForum');
      const s2 = document.getElementById('seqAboutTeam');
      const s3 = document.getElementById('seqAboutCollab');

      if (sec === 'all') {
        s1.style.display = 'block'; s2.style.display = 'block'; s3.style.display = 'block';
      } else if (sec === 'forum') {
        s1.style.display = 'block'; s2.style.display = 'none'; s3.style.display = 'none';
      } else if (sec === 'team') {
        s1.style.display = 'none'; s2.style.display = 'block'; s3.style.display = 'none';
      } else if (sec === 'collab') {
        s1.style.display = 'none'; s2.style.display = 'none'; s3.style.display = 'block';
      }
    }

    function filterResourcesSequence(cat, btn) {
      document.querySelectorAll('#resourcesModal .sub-pill-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const s1 = document.getElementById('seqSectionReport');
      const s2 = document.getElementById('seqSectionPublication');
      const s3 = document.getElementById('seqSectionBylaws');

      if (cat === 'all') {
        s1.style.display = 'block'; s2.style.display = 'block'; s3.style.display = 'block';
      } else if (cat === 'Report') {
        s1.style.display = 'block'; s2.style.display = 'none'; s3.style.display = 'none';
      } else if (cat === 'Publication') {
        s1.style.display = 'none'; s2.style.display = 'block'; s3.style.display = 'none';
      } else if (cat === 'By-Laws') {
        s1.style.display = 'none'; s2.style.display = 'none'; s3.style.display = 'block';
      }
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop.active').forEach(m => m.classList.remove('active'));
      }
      if (document.getElementById('galleryLightboxModal').classList.contains('active')) {
        if (e.key === 'ArrowLeft') prevGalleryPhoto();
        if (e.key === 'ArrowRight') nextGalleryPhoto();
      }
    });
  