<StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
  <NamedLayer>
    <Name>data_idh_dist</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <Name>Primer Quintil (0.6944 - 0.8452)</Name>
          <ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>cod_quint</ogc:PropertyName><ogc:Literal>1 </ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#4f6327</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#686868</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke>
          </PolygonSymbolizer>






        </Rule>
        <Rule>
          <Name>Segundo Quintil (0.5436 - 0.6944)</Name>
          <ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>cod_quint</ogc:PropertyName><ogc:Literal>2</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#c3d79a</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#686868</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>Tercer Quintil (0.3928 - 0.5436)</Name>
          <ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>cod_quint</ogc:PropertyName><ogc:Literal>3</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#ffd5b4</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#686868</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>Cuarto Quintil (0.2420 - 0.3928)</Name>
          <ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>cod_quint</ogc:PropertyName><ogc:Literal>4</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#e26c0a</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#686868</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <Name>Quinto Quintil (0.0912 - 0.2420)</Name>
          <ogc:Filter><ogc:PropertyIsEqualTo><ogc:PropertyName>cod_quint</ogc:PropertyName><ogc:Literal>5</ogc:Literal></ogc:PropertyIsEqualTo></ogc:Filter>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#974806</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#686868</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        
        
        
        <Rule>

          <MaxScaleDenominator>1000000</MaxScaleDenominator>
          
          <TextSymbolizer>
            <Label><ogc:PropertyName>nom_dist</ogc:PropertyName></Label>
            <Font>
              <CssParameter name="font-family">Calibri</CssParameter>
              <CssParameter name="font-weight">bold</CssParameter>
              <!--CssParameter name="font-style">oblique</CssParameter-->
              <CssParameter name="font-size">7</CssParameter>

            </Font>
            <LabelPlacement>
              <PointPlacement>
                <AnchorPoint>
                  <AnchorPointX>0.5</AnchorPointX>
                  <AnchorPointY>0.5</AnchorPointY>
                </AnchorPoint>
              </PointPlacement>
            </LabelPlacement>
            <Halo>
              <Radius>0.5</Radius>

              <Fill>
                <CssParameter name="fill">#ffffff</CssParameter>

              </Fill>
            </Halo>

            <Fill>
              <CssParameter name="fill">#686868</CssParameter>
            </Fill>
          </TextSymbolizer>

        </Rule>
        
        
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>